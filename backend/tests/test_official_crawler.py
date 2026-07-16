from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.services import official_crawler
from app.services.official_crawler import CrawlError, DiscoveredJob, next_daily_crawl


def register_admin(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "owner@example.com",
            "password": "strong-pass-123",
            "full_name": "同步管理员",
        },
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_parsers_extract_official_links() -> None:
    html = """
    <a href="/campus/jobs/1">2027 校园招聘 - 后端工程师</a>
    <a href="/about">企业介绍</a>
    """.encode()
    html_items = official_crawler.parse_html_links(
        html, "https://careers.example.com/list", ["校园招聘"]
    )
    assert html_items == [
        DiscoveredJob(
            title="2027 校园招聘 - 后端工程师",
            application_url="https://careers.example.com/campus/jobs/1",
        )
    ]

    rss = b"""<?xml version="1.0"?>
    <rss><channel><item><title>AI Engineer</title>
    <link>https://careers.example.com/jobs/ai</link>
    <pubDate>Wed, 15 Jul 2026 08:00:00 GMT</pubDate>
    </item></channel></rss>"""
    rss_items = official_crawler.parse_xml_feed(rss, "https://careers.example.com/feed")
    assert rss_items[0].title == "AI Engineer"
    assert rss_items[0].published_at == datetime(2026, 7, 15, 8, tzinfo=UTC)

    baidu = b"""<script>window.__INITIAL_DATA__ ={
      "listData":{"listDetailData":[{
        "name":"2027AIDU-Agent Engineer(J1)",
        "postId":"11111111-2222-3333-4444-555555555555",
        "postType":"Technology",
        "publishDate":"2026-07-16",
        "workPlace":"Beijing",
        "workContent":"Build agents",
        "serviceCondition":"Computer science"
      }]},"unused":undefined}; window.prefix="/jobs";</script>"""
    baidu_items = official_crawler.parse_baidu_ssr(
        baidu, "https://talent.baidu.com/jobs/list?recruitType=GRADUATE"
    )
    assert baidu_items == [
        DiscoveredJob(
            title="2027AIDU-Agent Engineer(J1)",
            application_url=(
                "https://talent.baidu.com/jobs/detail/GRADUATE/11111111-2222-3333-4444-555555555555"
            ),
            published_at=datetime(2026, 7, 16, tzinfo=UTC),
            category="Technology",
            work_cities="Beijing",
            description="Build agents",
            requirements="Computer science",
        )
    ]


def test_crawler_rejects_private_network_targets() -> None:
    with pytest.raises(CrawlError, match="内网"):
        official_crawler.validate_public_url("http://127.0.0.1:8000/jobs")


def test_next_daily_crawl_uses_shanghai_five_am() -> None:
    before_five = datetime(2026, 7, 16, 20, 0, tzinfo=UTC)
    after_five = datetime(2026, 7, 16, 22, 0, tzinfo=UTC)

    assert next_daily_crawl(before_five, hour=5, timezone_name="Asia/Shanghai") == datetime(
        2026, 7, 16, 21, 0, tzinfo=UTC
    )
    assert next_daily_crawl(after_five, hour=5, timezone_name="Asia/Shanghai") == datetime(
        2026, 7, 17, 21, 0, tzinfo=UTC
    )


def test_admin_can_sync_discovered_job_and_link(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    headers = register_admin(client)
    company = client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "name": "官方同步测试企业",
            "industry": "人工智能",
            "company_type": "民营企业",
            "education_requirement": "待核验",
            "work_cities": "待核验",
        },
    )
    assert company.status_code == 201, company.text
    source = client.post(
        "/api/v1/admin/data-sources",
        headers=headers,
        json={
            "name": "测试企业官方招聘页",
            "source_type": "official_recruitment",
            "authorization_note": "企业官方测试来源，已确认允许用于本地自动化测试",
            "company_id": company.json()["id"],
            "feed_url": "https://talent.baidu.com/jobs/list?recruitType=GRADUATE",
            "parser_mode": "html_links",
            "is_crawl_enabled": True,
            "crawl_interval_minutes": 60,
        },
    )
    assert source.status_code == 201, source.text

    monkeypatch.setattr(
        official_crawler,
        "_discover",
        lambda _source: [
            DiscoveredJob(
                title="2027 届 AI 工程师",
                application_url="https://careers.example.com/apply/ai-2027",
            )
        ],
    )
    monkeypatch.setattr(official_crawler, "validate_public_url", lambda _url: None)

    run = client.post(f"/api/v1/admin/data-sources/{source.json()['id']}/crawl", headers=headers)
    assert run.status_code == 200, run.text
    assert run.json()["status"] == "completed"
    assert run.json()["discovered_rows"] == 1

    jobs = client.get("/api/v1/jobs?search=AI%20工程师", headers=headers)
    assert jobs.status_code == 200
    item = jobs.json()["items"][0]
    assert item["application_url"] == "https://careers.example.com/apply/ai-2027"
    assert item["recruitment_status"] == "unverified"
    assert item["last_verified_at"] is None

    second_run = client.post(
        f"/api/v1/admin/data-sources/{source.json()['id']}/crawl", headers=headers
    )
    assert second_run.json()["discovered_rows"] == 0
    assert second_run.json()["skipped_rows"] == 1


def test_trusted_official_adapter_publishes_structured_job(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    headers = register_admin(client)
    company = client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "name": "可信适配器测试企业",
            "industry": "人工智能",
            "company_type": "测试",
            "education_requirement": "官网为准",
            "work_cities": "北京",
        },
    )
    source = client.post(
        "/api/v1/admin/data-sources",
        headers=headers,
        json={
            "name": "可信官方适配器",
            "source_type": "trusted_official_adapter",
            "authorization_note": "企业官网结构化校招列表测试",
            "company_id": company.json()["id"],
            "feed_url": "https://talent.baidu.com/jobs/list?recruitType=GRADUATE",
            "parser_mode": "baidu_ssr",
            "is_crawl_enabled": True,
            "crawl_interval_minutes": 1440,
        },
    )
    monkeypatch.setattr(
        official_crawler,
        "_discover",
        lambda _source: [
            DiscoveredJob(
                title="2027 结构化官方岗位",
                application_url=(
                    "https://talent.baidu.com/jobs/detail/GRADUATE/"
                    "11111111-2222-3333-4444-555555555555"
                ),
                category="技术",
                work_cities="北京",
                description="官方职责",
                requirements="官方要求",
            )
        ],
    )
    monkeypatch.setattr(official_crawler, "validate_public_url", lambda _url: None)

    run = client.post(f"/api/v1/admin/data-sources/{source.json()['id']}/crawl", headers=headers)
    jobs = client.get(
        "/api/v1/jobs",
        params={"search": "结构化官方岗位", "verified_only": True},
    )

    assert run.status_code == 200
    assert jobs.status_code == 200
    assert jobs.json()["total"] == 1
    assert jobs.json()["items"][0]["recruitment_status"] == "open"
    assert jobs.json()["items"][0]["last_verified_at"] is not None
