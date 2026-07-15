from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models import Company, Job

DEMO_SOURCE = "demo_seed_not_realtime"
DEMO_STATUS = "demo_only"

INDUSTRIES: tuple[tuple[str, str, bool], ...] = (
    ("互联网", "民营企业", False),
    ("人工智能", "民营企业", False),
    ("通信", "国有企业", True),
    ("半导体", "民营企业", False),
    ("新能源", "民营企业", True),
    ("制造业", "国有企业", True),
    ("银行", "股份制企业", False),
    ("央企国企", "中央企业", False),
    ("医药", "民营企业", False),
    ("物流", "民营企业", True),
)
PREFIXES: tuple[str, ...] = ("启航", "星云", "远景")
CITIES: tuple[str, ...] = (
    "北京、上海",
    "深圳、杭州",
    "武汉、成都",
    "南京、苏州",
    "合肥、宁德",
)
JOB_TITLES: tuple[tuple[str, str], ...] = (
    ("软件开发工程师", "技术研发"),
    ("产品运营专员", "产品运营"),
)


def seed() -> None:
    """Idempotently create 30 companies and 60 jobs that are explicitly demo-only."""
    created_companies = 0
    created_jobs = 0
    with SessionLocal.begin() as db:
        existing_companies = {
            company.name: company
            for company in db.scalars(select(Company).where(Company.data_source == DEMO_SOURCE))
        }
        demo_companies: list[Company] = []

        for industry_index, (industry, company_type, accepts_college) in enumerate(INDUSTRIES):
            for prefix_index, prefix in enumerate(PREFIXES):
                name = f"{prefix}{industry}示例公司（Demo）"
                company = existing_companies.get(name)
                if company is None:
                    company = Company(
                        name=name,
                        industry=industry,
                        company_type=company_type,
                        website=None,
                        campus_website=None,
                        logo_url=None,
                        recruitment_status=DEMO_STATUS,
                        open_date=None,
                        deadline=None,
                        education_requirement=("专科及以上" if accepts_college else "本科及以上"),
                        accepts_college=accepts_college,
                        accepts_bachelor=True,
                        major_requirement="Demo：专业不限或相关专业，不代表真实招聘要求。",
                        work_cities=CITIES[(industry_index + prefix_index) % len(CITIES)],
                        data_source=DEMO_SOURCE,
                        last_verified_at=None,
                        is_demo=True,
                    )
                    db.add(company)
                    created_companies += 1
                else:
                    company.recruitment_status = DEMO_STATUS
                    company.open_date = None
                    company.deadline = None
                    company.last_verified_at = None
                    company.is_demo = True
                demo_companies.append(company)

        db.flush()
        for company in demo_companies:
            existing_jobs = {
                job.title: job
                for job in db.scalars(
                    select(Job).where(
                        Job.company_id == company.id,
                        Job.data_source == DEMO_SOURCE,
                    )
                )
            }
            for title, category in JOB_TITLES:
                demo_title = f"{title}（Demo）"
                existing_job = existing_jobs.get(demo_title)
                if existing_job is not None:
                    existing_job.recruitment_status = DEMO_STATUS
                    existing_job.published_at = None
                    existing_job.deadline = None
                    existing_job.application_url = None
                    existing_job.last_verified_at = None
                    existing_job.is_demo = True
                    continue
                db.add(
                    Job(
                        title=demo_title,
                        company_id=company.id,
                        category=category,
                        work_cities=company.work_cities,
                        education_requirement=company.education_requirement,
                        major_requirement="Demo：计算机、电子、经管等相关专业。",
                        description=(
                            "仅用于展示 OfferPilot 功能的 Demo 岗位，不代表示例企业存在或正在招聘。"
                        ),
                        requirements=(
                            "Demo：具备良好学习能力与协作意识；实际要求请以企业官方渠道为准。"
                        ),
                        application_url=None,
                        published_at=None,
                        deadline=None,
                        recruitment_status=DEMO_STATUS,
                        data_source=DEMO_SOURCE,
                        last_verified_at=None,
                        is_demo=True,
                    )
                )
                created_jobs += 1

        db.flush()
        company_total = (
            db.scalar(select(func.count(Company.id)).where(Company.data_source == DEMO_SOURCE)) or 0
        )
        job_total = db.scalar(select(func.count(Job.id)).where(Job.data_source == DEMO_SOURCE)) or 0

    print(
        f"Demo seed ready: {company_total} companies and {job_total} jobs "
        f"({created_companies} companies, {created_jobs} jobs created)."
    )


if __name__ == "__main__":
    seed()
