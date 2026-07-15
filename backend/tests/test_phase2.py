from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import settings


def register(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "phase2@example.com",
            "password": "strong-pass-123",
            "full_name": "二期用户",
        },
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_job(client: TestClient, headers: dict[str, str]) -> int:
    company = client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "name": "二期测试企业",
            "industry": "人工智能",
            "company_type": "民营企业",
            "recruitment_status": "open",
            "education_requirement": "本科及以上",
            "work_cities": "上海",
            "data_source": "phase2_test",
            "is_demo": False,
        },
    )
    job = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={
            "title": "二期后端工程师",
            "company_id": company.json()["id"],
            "category": "技术研发",
            "work_cities": "上海",
            "education_requirement": "本科及以上",
            "description": "测试岗位",
            "requirements": "熟悉 Python",
            "recruitment_status": "open",
            "data_source": "phase2_test",
            "deadline": (datetime.now(UTC) + timedelta(days=3)).isoformat(),
            "is_demo": False,
        },
    )
    assert job.status_code == 201, job.text
    return int(job.json()["id"])


def test_profile_resume_application_and_audit(client: TestClient, tmp_path: Path) -> None:
    settings.upload_dir = str(tmp_path / "uploads")
    headers = register(client)
    profile = client.patch(
        "/api/v1/auth/me",
        headers=headers,
        json={
            "graduation_year": 2027,
            "education_level": "本科",
            "target_cities": "上海、杭州",
            "notifications_enabled": True,
        },
    )
    assert profile.status_code == 200
    assert profile.json()["graduation_year"] == 2027

    uploaded = client.post(
        "/api/v1/resumes",
        headers=headers,
        data={"name": "后端方向简历", "version": "v2", "is_default": "true"},
        files={"file": ("resume.pdf", b"%PDF-1.4 phase2", "application/pdf")},
    )
    assert uploaded.status_code == 201, uploaded.text
    resume_id = int(uploaded.json()["id"])
    assert uploaded.json()["is_default"] is True
    assert client.get(f"/api/v1/resumes/{resume_id}/download", headers=headers).status_code == 200

    job_id = create_job(client, headers)
    application = client.post(
        "/api/v1/applications",
        headers=headers,
        json={"job_id": job_id, "resume_id": resume_id, "status": "applied"},
    )
    assert application.status_code == 201
    invalid = client.patch(
        f"/api/v1/applications/{application.json()['id']}",
        headers=headers,
        json={"status": "completed"},
    )
    assert invalid.status_code == 409
    audit = client.get("/api/v1/audit-logs", headers=headers)
    assert audit.status_code == 200
    assert audit.json()["total"] >= 3


def test_alerts_and_reminders_create_scoped_notifications(client: TestClient) -> None:
    headers = register(client)
    job_id = create_job(client, headers)
    favorite = client.post("/api/v1/favorites", headers=headers, json={"job_id": job_id})
    assert favorite.status_code == 201

    alert = client.post(
        "/api/v1/job-alerts",
        headers=headers,
        json={
            "name": "上海技术岗",
            "criteria": {"keyword": "二期", "city": "上海"},
            "frequency": "daily",
        },
    )
    assert alert.status_code == 201, alert.text
    alert_id = int(alert.json()["id"])
    matches = client.get(f"/api/v1/job-alerts/{alert_id}/matches", headers=headers)
    assert matches.json()["total"] == 1
    run_alert = client.post(f"/api/v1/job-alerts/{alert_id}/run", headers=headers)
    assert run_alert.json()["notifications_created"] == 1

    application = client.post(
        "/api/v1/applications",
        headers=headers,
        json={"job_id": job_id, "status": "applied"},
    )
    application_id = int(application.json()["id"])
    interview = client.post(
        "/api/v1/interviews",
        headers=headers,
        json={
            "application_id": application_id,
            "interview_type": "技术面",
            "scheduled_at": (datetime.now(UTC) + timedelta(hours=12)).isoformat(),
        },
    )
    assert interview.status_code == 201
    offer = client.post(
        "/api/v1/offers",
        headers=headers,
        json={
            "application_id": application_id,
            "received_at": date.today().isoformat(),
            "response_deadline": (date.today() + timedelta(days=2)).isoformat(),
        },
    )
    assert offer.status_code == 201
    reminder = client.post("/api/v1/reminders/run", headers=headers)
    assert reminder.status_code == 200
    assert reminder.json() == {"created": 3, "job_deadlines": 1, "interviews": 1, "offers": 1}
    notifications = client.get("/api/v1/notifications", headers=headers)
    assert notifications.json()["total"] == 4
