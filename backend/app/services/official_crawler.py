from __future__ import annotations

import ipaddress
import json
import socket
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.robotparser import RobotFileParser

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Company, CrawlRun, DataSource, Job

DEFAULT_KEYWORDS = ["校招", "校园招聘", "应届", "招聘", "graduate", "campus", "career", "job"]
ALLOWED_CONTENT_TYPES = {
    "application/atom+xml",
    "application/feed+json",
    "application/json",
    "application/rss+xml",
    "application/xml",
    "text/html",
    "text/plain",
    "text/xml",
}


class CrawlError(ValueError):
    pass


@dataclass(frozen=True)
class DiscoveredJob:
    title: str
    application_url: str
    published_at: datetime | None = None


class _RecruitmentLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._href: str | None = None
        self._parts: list[str] = []
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        self._href = dict(attrs).get("href")
        self._parts = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href is not None:
            self.links.append((self._href, " ".join(self._parts).strip()))
            self._href = None
            self._parts = []


def validate_public_url(url: str) -> None:
    parsed = urlparse(url)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise CrawlError("仅允许无凭据的公开 HTTP(S) 官方地址")
    try:
        addresses = socket.getaddrinfo(parsed.hostname, parsed.port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise CrawlError("招聘源域名无法解析") from exc
    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if not ip.is_global:
            raise CrawlError("招聘源不得指向本机、内网或保留地址")


class _SafeRedirectHandler(HTTPRedirectHandler):
    def redirect_request(
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> Request | None:
        validate_public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _fetch(url: str) -> tuple[bytes, str, str]:
    validate_public_url(url)
    request = Request(url, headers={"User-Agent": settings.crawler_user_agent})
    with build_opener(_SafeRedirectHandler()).open(
        request, timeout=settings.crawler_timeout_seconds
    ) as response:
        content_type = response.headers.get_content_type().lower()
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise CrawlError(f"不支持的响应类型：{content_type}")
        content = response.read(settings.crawler_max_response_bytes + 1)
        if len(content) > settings.crawler_max_response_bytes:
            raise CrawlError("招聘源响应超过本地安全大小限制")
        return content, content_type, response.geturl()


def _robots_allows(url: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        content, _, _ = _fetch(robots_url)
    except HTTPError as exc:
        if exc.code == 404:
            return True
        raise CrawlError(f"无法确认 robots.txt（HTTP {exc.code}）") from exc
    except OSError as exc:
        raise CrawlError("无法确认 robots.txt，已安全停止同步") from exc
    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(content.decode("utf-8", errors="replace").splitlines())
    return parser.can_fetch(settings.crawler_user_agent, url)


def parse_html_links(content: bytes, base_url: str, keywords: list[str]) -> list[DiscoveredJob]:
    parser = _RecruitmentLinkParser()
    parser.feed(content.decode("utf-8", errors="replace"))
    normalized_keywords = [item.strip().lower() for item in keywords if item.strip()]
    results: list[DiscoveredJob] = []
    seen: set[str] = set()
    for href, title in parser.links:
        absolute_url = urljoin(base_url, href)
        haystack = f"{title} {absolute_url}".lower()
        if (
            not title
            or not any(keyword in haystack for keyword in normalized_keywords)
            or absolute_url in seen
        ):
            continue
        parsed = urlparse(absolute_url)
        if parsed.scheme not in {"http", "https"}:
            continue
        seen.add(absolute_url)
        results.append(DiscoveredJob(title=title[:200], application_url=absolute_url))
    return results


def _first_text(element: ET.Element, names: set[str]) -> str | None:
    for child in element.iter():
        if child.tag.rsplit("}", 1)[-1].lower() in names and child.text:
            value = child.text.strip()
            if value:
                return value
    return None


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def parse_xml_feed(content: bytes, base_url: str) -> list[DiscoveredJob]:
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise CrawlError("官方 XML Feed 格式无效") from exc
    results: list[DiscoveredJob] = []
    for item in root.iter():
        if item.tag.rsplit("}", 1)[-1].lower() not in {"item", "entry"}:
            continue
        title = _first_text(item, {"title"})
        link = _first_text(item, {"link"})
        if not link:
            for child in item.iter():
                if child.tag.rsplit("}", 1)[-1].lower() == "link":
                    link = child.attrib.get("href")
                    if link:
                        break
        if not title or not link:
            continue
        results.append(
            DiscoveredJob(
                title=title[:200],
                application_url=urljoin(base_url, link),
                published_at=_parse_date(
                    _first_text(item, {"published", "updated", "pubdate", "date"})
                ),
            )
        )
    return results


def parse_json_feed(content: bytes, base_url: str) -> list[DiscoveredJob]:
    try:
        payload = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CrawlError("官方 JSON Feed 格式无效") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise CrawlError("JSON Feed 缺少 items 列表")
    results: list[DiscoveredJob] = []
    for raw in payload["items"]:
        if not isinstance(raw, dict):
            continue
        title = raw.get("title")
        link = raw.get("external_url") or raw.get("url")
        if not isinstance(title, str) or not isinstance(link, str):
            continue
        published = raw.get("date_published") or raw.get("date_modified")
        results.append(
            DiscoveredJob(
                title=title.strip()[:200],
                application_url=urljoin(base_url, link),
                published_at=_parse_date(published if isinstance(published, str) else None),
            )
        )
    return results


def _discover(source: DataSource) -> list[DiscoveredJob]:
    if not source.feed_url:
        raise CrawlError("未配置官方招聘源地址")
    if not _robots_allows(source.feed_url):
        raise CrawlError("robots.txt 不允许自动访问该招聘源")
    content, content_type, final_url = _fetch(source.feed_url)
    mode = source.parser_mode
    if mode == "auto":
        if content_type in {"application/json", "application/feed+json"}:
            mode = "json_feed"
        elif content_type == "text/html":
            mode = "html_links"
        else:
            mode = "rss"
    if mode == "html_links":
        return parse_html_links(content, final_url, source.link_keywords or DEFAULT_KEYWORDS)
    if mode == "json_feed":
        return parse_json_feed(content, final_url)
    return parse_xml_feed(content, final_url)


def ingest_discoveries(
    db: Session, source: DataSource, discoveries: list[DiscoveredJob]
) -> tuple[int, int, int]:
    if source.company_id is None:
        raise CrawlError("数据源未绑定企业")
    company = db.get(Company, source.company_id)
    if company is None:
        raise CrawlError("绑定企业不存在")
    created = updated = skipped = 0
    for discovery in discoveries[: settings.crawler_max_items_per_run]:
        try:
            validate_public_url(discovery.application_url)
        except CrawlError:
            skipped += 1
            continue
        if not discovery.title.strip() or len(discovery.application_url) > 500:
            skipped += 1
            continue
        existing = db.scalar(
            select(Job).where(
                Job.is_demo.is_(False),
                or_(
                    Job.application_url == discovery.application_url,
                    (Job.company_id == company.id) & (Job.title == discovery.title),
                ),
            )
        )
        if existing:
            changed = existing.application_url != discovery.application_url
            if discovery.published_at and existing.published_at != discovery.published_at:
                existing.published_at = discovery.published_at
                changed = True
            existing.application_url = discovery.application_url
            existing.data_source = source.name
            existing.data_source_id = source.id
            if changed:
                existing.last_verified_at = None
                existing.recruitment_status = "unverified"
                updated += 1
            else:
                skipped += 1
            continue
        db.add(
            Job(
                title=discovery.title,
                company_id=company.id,
                category="待核验",
                work_cities="待核验",
                education_requirement="待核验",
                description="自动同步发现，详情请访问官方投递页面并由管理员核验。",
                requirements="待核验",
                application_url=discovery.application_url,
                published_at=discovery.published_at,
                recruitment_status="unverified",
                data_source=source.name,
                data_source_id=source.id,
                last_verified_at=None,
                is_demo=False,
            )
        )
        created += 1
    skipped += max(0, len(discoveries) - settings.crawler_max_items_per_run)
    return created, updated, skipped


def run_source_crawl(db: Session, source: DataSource) -> CrawlRun:
    now = datetime.now(UTC)
    run = CrawlRun(source_id=source.id, status="running", started_at=now)
    db.add(run)
    db.flush()
    try:
        discoveries = _discover(source)
        created, updated, skipped = ingest_discoveries(db, source, discoveries)
        run.status = "completed"
        run.discovered_rows = created
        run.updated_rows = updated
        run.skipped_rows = skipped
        source.last_crawl_status = "completed"
    except Exception as exc:
        run.status = "failed"
        run.error_message = str(exc)[:2000]
        source.last_crawl_status = "failed"
    finished = datetime.now(UTC)
    run.finished_at = finished
    source.last_crawled_at = finished
    source.next_crawl_at = finished + timedelta(minutes=source.crawl_interval_minutes)
    db.commit()
    db.refresh(run)
    return run


def run_due_crawls(db: Session) -> None:
    now = datetime.now(UTC)
    sources = list(
        db.scalars(
            select(DataSource).where(
                DataSource.is_active.is_(True),
                DataSource.is_crawl_enabled.is_(True),
                or_(DataSource.next_crawl_at.is_(None), DataSource.next_crawl_at <= now),
            )
        )
    )
    for source in sources:
        run_source_crawl(db, source)
