from fastapi.testclient import TestClient


def register(client: TestClient, email: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "strong-pass-123", "full_name": "治理测试"},
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_admin_csv_import_review_and_quality(client: TestClient) -> None:
    headers = register(client, "admin@example.com")
    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.json()["is_admin"] is True

    demo = client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "name": "可信示例企业",
            "industry": "演示行业",
            "company_type": "Demo",
            "education_requirement": "演示",
            "work_cities": "演示",
            "is_demo": True,
        },
    )
    assert demo.status_code == 201

    source = client.post(
        "/api/v1/admin/data-sources",
        headers=headers,
        json={
            "name": "校方授权导出",
            "source_type": "authorized_csv",
            "authorization_note": "已获得校方就业中心用于本地测试的明确授权",
        },
    )
    assert source.status_code == 201, source.text
    source_id = source.json()["id"]

    company_csv = (
        "name,industry,company_type,education_requirement,work_cities,accepts_bachelor\n"
        "可信示例企业,制造业,国有企业,本科及以上,上海,true\n"
    )
    imported = client.post(
        "/api/v1/admin/imports",
        headers=headers,
        data={"source_id": source_id, "entity_type": "company"},
        files={"file": ("companies.csv", company_csv.encode(), "text/csv")},
    )
    assert imported.status_code == 201, imported.text
    assert imported.json()["created_rows"] == 1
    assert imported.json()["error_rows"] == 0

    queue = client.get("/api/v1/admin/review?entity_type=company", headers=headers).json()
    assert queue["total"] == 1
    item_id = queue["items"][0]["id"]
    reviewed = client.patch(
        f"/api/v1/admin/review/company/{item_id}",
        headers=headers,
        json={"action": "approve", "recruitment_status": "open"},
    )
    assert reviewed.status_code == 200, reviewed.text
    assert reviewed.json()["last_verified_at"] is not None

    quality = client.get("/api/v1/admin/quality", headers=headers)
    assert quality.status_code == 200
    assert quality.json()["verified_records"] == 1
    assert quality.json()["demo_records"] == 1
    assert quality.json()["source_coverage"][0]["companies"] == 1


def test_non_admin_cannot_mutate_global_catalog(client: TestClient) -> None:
    headers = register(client, "regular@example.com")
    response = client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "name": "无权限企业",
            "industry": "互联网",
            "company_type": "民营企业",
            "education_requirement": "本科",
            "work_cities": "北京",
        },
    )
    assert response.status_code == 403
    assert client.get("/api/v1/admin/quality", headers=headers).status_code == 403
