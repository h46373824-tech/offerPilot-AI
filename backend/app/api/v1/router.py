from fastapi import APIRouter

from app.api.v1.routes import (
    activity,
    applications,
    auth,
    companies,
    dashboard,
    favorites,
    interviews,
    job_alerts,
    jobs,
    notifications,
    offers,
    resumes,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(companies.router)
api_router.include_router(jobs.router)
api_router.include_router(favorites.router)
api_router.include_router(applications.router)
api_router.include_router(interviews.router)
api_router.include_router(offers.router)
api_router.include_router(notifications.router)
api_router.include_router(dashboard.router)
api_router.include_router(resumes.router)
api_router.include_router(job_alerts.router)
api_router.include_router(activity.router)
