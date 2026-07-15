from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.services import official_crawler
from app.services.official_crawler import CrawlError, DiscoveredJob


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


def test_crawler_rejects_private_network_targets() -> None:
    with pytest.raises(CrawlError, match="内网"):
        official_crawler.validate_public_url("http://127.0.0.1:8000/jobs")


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
            "feed_url": "https://careers.example.com/jobs",
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
