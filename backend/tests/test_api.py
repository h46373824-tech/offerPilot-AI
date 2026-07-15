from datetime import UTC, date, datetime, timedelta
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.db.seed import DEMO_SOURCE, seed
from app.db.session import SessionLocal
from app.models import Company, Job, Notification, User


def register(
    client: TestClient,
    email: str = "student@example.com",
    password: str = "strong-pass-123",
) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "测试同学"},
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_company_and_job(client: TestClient, headers: dict[str, str]) -> tuple[int, int]:
    company_response = client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "name": "测试科技公司",
            "industry": "人工智能",
            "company_type": "民营企业",
            "recruitment_status": "open",
            "education_requirement": "本科及以上",
            "accepts_bachelor": True,
            "work_cities": "北京",
            "data_source": "manual_test",
            "is_demo": False,
        },
    )
    assert company_response.status_code == 201, company_response.text
    company_id = int(company_response.json()["id"])
    job_response = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={
            "title": "后端开发工程师",
            "company_id": company_id,
            "category": "技术研发",
            "work_cities": "北京",
            "education_requirement": "本科及以上",
            "description": "负责服务端开发",
            "requirements": "熟悉 Python",
            "recruitment_status": "open",
            "data_source": "manual_test",
            "deadline": (datetime.now(UTC) + timedelta(days=7)).isoformat(),
            "is_demo": False,
        },
    )
    assert job_response.status_code == 201, job_response.text
    return company_id, int(job_response.json()["id"])


def test_health_and_openapi_oauth2_configuration(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "offerpilot-api"}

    schema_response = client.get("/openapi.json")
    assert schema_response.status_code == 200
    schema = schema_response.json()
    password_flow = schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]["flows"]
    assert password_flow["password"]["tokenUrl"] == "/api/v1/auth/token"


def test_register_json_login_oauth2_login_and_me(client: TestClient) -> None:
    email = "Student@Example.com"
    password = "strong-pass-123"
    headers = register(client, email=email, password=password)

    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == email.lower()
    assert client.get("/api/v1/auth/me").status_code == 401

    duplicate = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "重复用户"},
    )
    assert duplicate.status_code == 409
    wrong_password = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "incorrect-password"},
    )
    assert wrong_password.status_code == 401

    json_login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert json_login.status_code == 200
    oauth_login = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": password},
    )
    assert oauth_login.status_code == 200
    assert oauth_login.json()["token_type"] == "bearer"


def test_company_and_job_crud_search_filter_and_pagination(client: TestClient) -> None:
    assert client.get("/api/v1/companies").status_code == 401
    headers = register(client)
    company_id, job_id = create_company_and_job(client, headers)

    companies = client.get(
        "/api/v1/companies",
        headers=headers,
        params={"search": "测试科技", "industry": "人工智能", "is_demo": "false"},
    )
    assert companies.status_code == 200
    assert companies.json()["total"] == 1
    assert companies.json()["pages"] == 1

    company_patch = client.patch(
        f"/api/v1/companies/{company_id}",
        headers=headers,
        json={"work_cities": "北京、上海"},
    )
    assert company_patch.status_code == 200
    assert company_patch.json()["work_cities"] == "北京、上海"
    invalid_patch = client.patch(
        f"/api/v1/companies/{company_id}", headers=headers, json={"name": None}
    )
    assert invalid_patch.status_code == 422

    jobs = client.get(
        "/api/v1/jobs",
        headers=headers,
        params={"search": "测试科技", "category": "技术研发", "sort_by": "title"},
    )
    assert jobs.status_code == 200
    assert jobs.json()["total"] == 1

    job_patch = client.patch(
        f"/api/v1/jobs/{job_id}",
        headers=headers,
        json={"title": "高级后端开发工程师"},
    )
    assert job_patch.status_code == 200
    missing_company = client.patch(
        f"/api/v1/jobs/{job_id}", headers=headers, json={"company_id": 99999}
    )
    assert missing_company.status_code == 404

    assert client.delete(f"/api/v1/jobs/{job_id}", headers=headers).status_code == 204
    assert client.delete(f"/api/v1/companies/{company_id}", headers=headers).status_code == 204


def test_application_favorite_interview_and_offer_lifecycle(client: TestClient) -> None:
    headers = register(client)
    _, job_id = create_company_and_job(client, headers)

    favorite = client.post("/api/v1/favorites", headers=headers, json={"job_id": job_id})
    assert favorite.status_code == 201
    assert client.get("/api/v1/favorites", headers=headers).json()["total"] == 1

    application = client.post(
        "/api/v1/applications",
        headers=headers,
        json={"job_id": job_id, "status": "applied", "channel": "企业官网"},
    )
    assert application.status_code == 201
    application_id = int(application.json()["id"])
    application_page = client.get(
        "/api/v1/applications", headers=headers, params={"status": "applied"}
    )
    assert application_page.json()["total"] == 1

    interview = client.post(
        "/api/v1/interviews",
        headers=headers,
        json={
            "application_id": application_id,
            "interview_type": "技术一面",
            "scheduled_at": (datetime.now(UTC) + timedelta(days=2)).isoformat(),
        },
    )
    assert interview.status_code == 201
    interview_id = int(interview.json()["id"])
    interview_patch = client.patch(
        f"/api/v1/interviews/{interview_id}",
        headers=headers,
        json={"status": "completed"},
    )
    assert interview_patch.status_code == 200

    offer = client.post(
        "/api/v1/offers",
        headers=headers,
        json={
            "application_id": application_id,
            "status": "pending",
            "received_at": date.today().isoformat(),
        },
    )
    assert offer.status_code == 201
    offer_id = int(offer.json()["id"])
    offer_patch = client.patch(
        f"/api/v1/offers/{offer_id}", headers=headers, json={"status": "accepted"}
    )
    assert offer_patch.status_code == 200
    assert client.get("/api/v1/offers", headers=headers).json()["total"] == 1

    dashboard = client.get("/api/v1/dashboard/stats", headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["applications"] == 1
    assert dashboard.json()["interviews"] == 1
    assert dashboard.json()["offers"] == 1
    assert dashboard.json()["recent_applications"][0]["job_title"] == "后端开发工程师"

    assert client.delete(f"/api/v1/offers/{offer_id}", headers=headers).status_code == 204
    assert client.delete(f"/api/v1/interviews/{interview_id}", headers=headers).status_code == 204
    assert (
        client.delete(f"/api/v1/applications/{application_id}", headers=headers).status_code == 204
    )
    assert client.delete(f"/api/v1/favorites/{job_id}", headers=headers).status_code == 204


def test_user_cannot_access_another_users_application(client: TestClient) -> None:
    owner_headers = register(client, email="owner@example.com")
    _, job_id = create_company_and_job(client, owner_headers)
    application = client.post(
        "/api/v1/applications", headers=owner_headers, json={"job_id": job_id}
    )
    application_id = int(application.json()["id"])

    other_headers = register(client, email="other@example.com")
    assert (
        client.get(f"/api/v1/applications/{application_id}", headers=other_headers).status_code
        == 404
    )
    cross_user_interview = client.post(
        "/api/v1/interviews",
        headers=other_headers,
        json={
            "application_id": application_id,
            "interview_type": "技术面",
            "scheduled_at": datetime.now(UTC).isoformat(),
        },
    )
    assert cross_user_interview.status_code == 404


def test_notifications_are_scoped_and_can_be_marked_read(client: TestClient) -> None:
    headers = register(client)
    with SessionLocal.begin() as db:
        user_id = db.scalar(select(User.id).where(User.email == "student@example.com"))
        assert user_id is not None
        notification = Notification(
            user_id=user_id,
            title="截止提醒",
            content="这是测试通知",
            notification_type="deadline",
        )
        db.add(notification)
        db.flush()
        notification_id = notification.id

    unread = client.get("/api/v1/notifications", headers=headers, params={"unread_only": "true"})
    assert unread.status_code == 200
    assert unread.json()["total"] == 1
    marked = client.patch(f"/api/v1/notifications/{notification_id}/read", headers=headers)
    assert marked.status_code == 200
    assert marked.json()["is_read"] is True
    assert client.patch("/api/v1/notifications/read-all", headers=headers).status_code == 204


def test_demo_seed_is_idempotent_and_explicitly_non_realtime(client: TestClient) -> None:
    del client  # The fixture ensures the isolated test database is initialized.
    seed()
    seed()

    with SessionLocal() as db:
        company_count = db.scalar(
            select(func.count(Company.id)).where(Company.data_source == DEMO_SOURCE)
        )
        job_count = db.scalar(select(func.count(Job.id)).where(Job.data_source == DEMO_SOURCE))
        industries = set(
            db.scalars(select(Company.industry).where(Company.data_source == DEMO_SOURCE))
        )
        demo_companies = list(db.scalars(select(Company).where(Company.data_source == DEMO_SOURCE)))
        demo_jobs = list(db.scalars(select(Job).where(Job.data_source == DEMO_SOURCE)))

    assert company_count == 30
    assert job_count == 60
    assert industries == {
        "互联网",
        "人工智能",
        "通信",
        "半导体",
        "新能源",
        "制造业",
        "银行",
        "央企国企",
        "医药",
        "物流",
    }
    assert all(item.is_demo and item.recruitment_status == "demo_only" for item in demo_companies)
    assert all(item.is_demo and item.recruitment_status == "demo_only" for item in demo_jobs)
    assert all(item.application_url is None for item in demo_jobs)


def test_offer_rejects_invalid_date_range(client: TestClient) -> None:
    headers = register(client)
    _, job_id = create_company_and_job(client, headers)
    application = client.post("/api/v1/applications", headers=headers, json={"job_id": job_id})
    response = client.post(
        "/api/v1/offers",
        headers=headers,
        json={
            "application_id": application.json()["id"],
            "received_at": "2026-07-20",
            "response_deadline": "2026-07-19",
        },
    )
    assert response.status_code == 422


def test_api_does_not_expose_internal_password_hash(client: TestClient) -> None:
    headers = register(client)
    payload: dict[str, Any] = client.get("/api/v1/auth/me", headers=headers).json()
    assert "hashed_password" not in payload
