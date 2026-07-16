from __future__ import annotations

from datetime import UTC, date, datetime
from typing import TypedDict

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Company, DataSource, Job

OFFICIAL_SEED_KEY = "official_launch_verified_2026-07-16"
VERIFIED_AT = datetime(2026, 7, 16, 4, 0, tzinfo=UTC)


class JobSpec(TypedDict, total=False):
    title: str
    category: str
    cities: str
    education: str
    major: str
    description: str
    application_url: str
    open_date: str
    deadline: str


class CompanySpec(TypedDict):
    name: str
    industry: str
    company_type: str
    website: str
    campus_website: str
    cities: str
    evidence: str
    jobs: list[JobSpec]


def _campaign(
    title: str,
    category: str,
    application_url: str,
    description: str,
    *,
    cities: str = "全国/以官方岗位为准",
    education: str = "以官方岗位要求为准",
    major: str = "以官方岗位要求为准",
    open_date: str = "2026-07-01",
    deadline: str | None = None,
) -> JobSpec:
    result: JobSpec = {
        "title": title,
        "category": category,
        "cities": cities,
        "education": education,
        "major": major,
        "description": description,
        "application_url": application_url,
        "open_date": open_date,
    }
    if deadline:
        result["deadline"] = deadline
    return result


OFFICIAL_COMPANIES: tuple[CompanySpec, ...] = (
    {
        "name": "DJI 大疆",
        "industry": "智能硬件",
        "company_type": "民营企业",
        "website": "https://www.dji.com/cn",
        "campus_website": "https://careers.dji.com/zh-CN/campus",
        "cities": "深圳、上海及其他岗位城市",
        "evidence": "官方校招页明确：2027 拓疆者校园招聘于 2026-06-25 开启，招满即止。",
        "jobs": [
            _campaign(
                "2027“拓疆者”校园招聘岗位合集",
                "校园招聘",
                "https://apply.careers.dji.com/campus-recruitment/dji/143359?locale=zh-CN",
                "官方招聘项目入口；具体岗位、城市和要求以投递页面当前展示为准。",
                open_date="2026-06-25",
            )
        ],
    },
    {
        "name": "拼多多集团 PDD",
        "industry": "互联网",
        "company_type": "民营企业",
        "website": "https://www.pddholdings.com/",
        "campus_website": "https://careers.pddglobalhr.com/campus/",
        "cities": "以官方岗位为准",
        "evidence": "官方校招页明确面向 2026-09 至 2027-08 毕业生开放 2027 届校招。",
        "jobs": [
            _campaign(
                "2027届校园招聘岗位合集",
                "校园招聘",
                "https://careers.pddglobalhr.com/campus/",
                "面向 2026 年 9 月至 2027 年 8 月毕业生的官方应届生招聘入口。",
            ),
            _campaign(
                "大模型人才专项",
                "人工智能",
                "https://careers.pddglobalhr.com/campus/",
                "面向全球校园技术人才的大模型方向专项，具体职位以官网为准。",
                education="本科及以上/以官方岗位为准",
            ),
        ],
    },
    {
        "name": "百度",
        "industry": "人工智能",
        "company_type": "民营企业",
        "website": "https://home.baidu.com/",
        "campus_website": "https://talent.baidu.com/jobs/campus",
        "cities": "北京、上海、深圳等",
        "evidence": "官方校招页显示 2026-07-09 起网申，面向 2026-09 至 2027-08 毕业生。",
        "jobs": [
            _campaign(
                f"2027校园招聘·{category}类岗位",
                category,
                "https://talent.baidu.com/jobs/campus",
                f"百度官方确认开放的{category}类校园岗位，具体职位以官网筛选结果为准。",
                cities="北京、上海、深圳等",
                open_date="2026-07-09",
            )
            for category in ("技术", "产品", "政企", "销售", "综合")
        ],
    },
    {
        "name": "华为",
        "industry": "通信",
        "company_type": "民营企业",
        "website": "https://www.huawei.com/cn/",
        "campus_website": "https://career.huawei.com/cn/campus-recruitment",
        "cities": "全国及海外岗位城市",
        "evidence": "华为官方校园招聘页显示 2027 届顶尖 AI 人才专项及 2027 届实习招聘。",
        "jobs": [
            _campaign(
                "2027届顶尖AI人才招聘专项",
                "人工智能",
                "https://career.huawei.com/cn/campus-recruitment",
                "聚焦 AI、数智化、超级计算等方向，具体职位以华为官方页面为准。",
            ),
            _campaign(
                "2027届实习生招聘岗位合集",
                "实习生招聘",
                "https://career.huawei.com/cn/campus-recruitment",
                "主要面向 2027 届毕业在校生的官方实习招聘入口。",
            ),
        ],
    },
    {
        "name": "字节跳动",
        "industry": "互联网",
        "company_type": "民营企业",
        "website": "https://www.bytedance.com/zh/",
        "campus_website": "https://jobs.bytedance.com/campus/page-6272Gc",
        "cities": "北京、上海、深圳、杭州等",
        "evidence": "官方校招页显示 Seed 大模型人才校招面向 2027 届及以后毕业生。",
        "jobs": [
            _campaign(
                "Seed大模型人才校招岗位合集",
                "人工智能",
                "https://jobs.bytedance.com/campus/page-6272Gc",
                "覆盖基础大模型、机器学习系统、视觉、语音、AI 搜索与具身智能等方向。",
                cities="北京、上海、深圳、杭州等",
            )
        ],
    },
    {
        "name": "小米集团",
        "industry": "智能硬件",
        "company_type": "民营企业",
        "website": "https://www.mi.com/",
        "campus_website": "https://hr.xiaomi.com/campus/",
        "cities": "北京、武汉、南京、上海、深圳等",
        "evidence": "小米官方校招页当前展示面向 2024-2027 年毕业生的顶尖应届项目。",
        "jobs": [
            _campaign(
                "顶尖应届招聘岗位合集",
                "校园招聘",
                "https://hr.xiaomi.com/campus/",
                "小米官方顶尖应届招聘入口，具体岗位和投递状态以官网为准。",
                cities="北京、武汉、南京、上海、深圳等",
            )
        ],
    },
    {
        "name": "OPPO",
        "industry": "智能终端",
        "company_type": "民营企业",
        "website": "https://www.oppo.com/cn/",
        "campus_website": "https://careers.oppo.com/university/oppo/campus/",
        "cities": "深圳、东莞、成都、西安等",
        "evidence": "OPPO 官方岗位页当前展示 2027 届寻梦实习招聘。",
        "jobs": [
            _campaign(
                "2027届寻梦实习招聘岗位合集",
                "实习生招聘",
                "https://careers.oppo.com/university/oppo/campus/post",
                "OPPO 官方 2027 届实习岗位入口，具体岗位以当前列表为准。",
                cities="深圳、东莞、成都、西安等",
            )
        ],
    },
    {
        "name": "比亚迪",
        "industry": "新能源",
        "company_type": "民营企业",
        "website": "https://www.bydglobal.com/cn/",
        "campus_website": "https://job.byd.com/portal/mobile/school-home",
        "cities": "深圳、西安、合肥、长沙等",
        "evidence": "比亚迪官方校招页当前标明面向 2026 和 2027 届毕业生。",
        "jobs": [
            _campaign(
                "2026/2027届校园招聘岗位合集",
                "校园招聘",
                "https://job.byd.com/portal/mobile/school-home",
                "比亚迪官方校园招聘入口，岗位、专业和城市以官网当前信息为准。",
                cities="深圳、西安、合肥、长沙等",
            )
        ],
    },
    {
        "name": "联想集团",
        "industry": "智能制造",
        "company_type": "民营企业",
        "website": "https://www.lenovo.com.cn/",
        "campus_website": "https://talent.lenovo.com.cn/trainee",
        "cities": "北京、上海、深圳、武汉、合肥等",
        "evidence": "联想官方实习招聘页明确 2027 届毕业范围为 2026-09-01 至 2027-08-31。",
        "jobs": [
            _campaign(
                "2027届实习生招聘岗位合集",
                "实习生招聘",
                "https://talent.lenovo.com.cn/trainee",
                "联想官方实习生招聘入口，具体岗位和投递状态以官网为准。",
                cities="北京、上海、深圳、武汉、合肥等",
            )
        ],
    },
    {
        "name": "长江存储",
        "industry": "半导体",
        "company_type": "民营企业",
        "website": "https://www.ymtc.com/cn/",
        "campus_website": "https://ymtc-campus.zhiye.com/",
        "cities": "武汉、上海、北京",
        "evidence": "2026-07 发布的 2027 届提前批简章指向长江存储官方校招投递站。",
        "jobs": [
            _campaign(
                "2027届提前批校园招聘岗位合集",
                "半导体研发与制造",
                "https://ymtc-campus.zhiye.com/",
                "官方投递站包含电路设计、研发技术、量产技术、质量、市场和职能岗位。",
                cities="武汉、上海、北京",
                open_date="2026-07-01",
            )
        ],
    },
    {
        "name": "京东方 BOE",
        "industry": "半导体显示",
        "company_type": "股份制企业",
        "website": "https://www.boe.com/",
        "campus_website": "https://www.boe.com/join/index",
        "cities": "北京、合肥、成都、重庆、武汉、苏州等",
        "evidence": "京东方 2027 届先锋京英计划于 2026-07-02 启动，公开投递期至 2026-08-14。",
        "jobs": [
            _campaign(
                "2027届先锋京英计划",
                "校园招聘提前批",
                "https://www.boe.com/join/index",
                "面向 2027 届毕业生的京东方官方提前批入口，具体赛道以官网为准。",
                cities="北京、合肥、成都、重庆、武汉、苏州等",
                open_date="2026-07-02",
                deadline="2026-08-14",
            )
        ],
    },
    {
        "name": "海尔集团",
        "industry": "制造业",
        "company_type": "民营企业",
        "website": "https://www.haier.com/",
        "campus_website": "https://maker.haier.net/client/campus/index",
        "cities": "青岛、北京、上海、深圳及其他城市",
        "evidence": "海尔官方招聘页当前展示 2027 届岗位并提供具体职位申请页面。",
        "jobs": [
            _campaign(
                "智造技术工程师-卡奥斯",
                "智能制造",
                "https://maker.haier.net/client/campus/customizedjobdetail/id/78.html",
                "负责精益体系、制造效率和项目落地；岗位详情以海尔官方页面为准。",
                cities="青岛、合肥、佛山、重庆",
                education="本科及以上",
                major="工业工程、机械、机电等相关专业",
            ),
            _campaign(
                "MEDP-智造技术研发工程师",
                "技术研发",
                "https://maker.haier.net/client/campus/deliverfirst/id/47/fid/22/rid/397.html",
                "设备技术、工业大模型、视觉检测、具身智能和数字孪生等方向。",
                cities="青岛",
                education="硕士及以上",
                major="机械、自动化、控制、计算机、人工智能等相关专业",
            ),
            _campaign(
                "算法工程师（多模态）",
                "人工智能",
                "https://maker.haier.net/client/campus/deliverfirst/id/47/fid/30/rid/282.html",
                "多模态算法、计算机视觉及工业场景应用，详情以官方岗位页为准。",
                cities="青岛",
                education="硕士及以上",
                major="电子信息、计算机、软件、自动化、人工智能等相关专业",
            ),
            _campaign(
                "外贸销售",
                "市场销售",
                "https://maker.haier.net/client/campus/deliverfirst/id/48/fid/26/rid/484.html",
                "海外市场开发、商务谈判和订单跟进，详情以官方岗位页为准。",
                cities="上海",
                education="本科及以上",
                major="专业不限，国际贸易、工商管理、机械、电机等优先",
            ),
        ],
    },
    {
        "name": "中国航天科技集团",
        "industry": "央企国企",
        "company_type": "中央企业",
        "website": "https://www.spacechina.com/",
        "campus_website": "https://wap.sasac.gov.cn/n2588035/n2588325/n2588350/c35517299/content.html",
        "cities": "北京、上海、西安、成都、保定等",
        "evidence": "国务院国资委于 2026-06-30 发布航天科技集团 2027 校招提前批启动信息。",
        "jobs": [
            _campaign(
                "2027届星辰英才计划校招提前批",
                "央企校园招聘",
                "https://wap.sasac.gov.cn/n2588035/n2588325/n2588350/c35517299/content.html",
                "国资委官方发布的 2027 届提前批信息，具体单位与岗位按公告进入。",
                cities="北京、上海、西安、成都、保定等",
                open_date="2026-06-30",
            )
        ],
    },
    {
        "name": "基恩士中国",
        "industry": "工业自动化",
        "company_type": "外商投资企业",
        "website": "https://www.keyence.com.cn/",
        "campus_website": "https://www.keyence.com.cn/ss/careers/recruitment.jsp",
        "cities": "全国高校",
        "evidence": "基恩士中国官方招聘页当前展示 2027 校园大使招募和网申入口。",
        "jobs": [
            _campaign(
                "2027校园大使",
                "校园大使",
                "https://keyence.zhiye.com/",
                "参与校园社群、招聘活动与人才推荐，具体申请规则以官网为准。",
                education="本科及以上",
                major="专业不限",
            )
        ],
    },
)


def _published(value: str) -> datetime:
    return datetime.combine(date.fromisoformat(value), datetime.min.time(), tzinfo=UTC)


def _deadline(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(f"{value}T23:59:59+08:00")


def _needs_verification_update(value: datetime | None) -> bool:
    if value is None:
        return True
    normalized = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    return normalized < VERIFIED_AT


def seed_official() -> None:
    created_companies = created_jobs = 0
    with SessionLocal.begin() as db:
        for spec in OFFICIAL_COMPANIES:
            company = db.scalar(
                select(Company).where(Company.name == spec["name"], Company.is_demo.is_(False))
            )
            if company is None:
                company = Company(
                    name=spec["name"],
                    industry=spec["industry"],
                    company_type=spec["company_type"],
                    recruitment_status="open",
                    education_requirement="以官方岗位要求为准",
                    accepts_college=False,
                    accepts_bachelor=True,
                    work_cities=spec["cities"],
                    data_source=OFFICIAL_SEED_KEY,
                    last_verified_at=VERIFIED_AT,
                    is_demo=False,
                )
                db.add(company)
                db.flush()
                created_companies += 1
            company.industry = spec["industry"]
            company.company_type = spec["company_type"]
            company.website = spec["website"]
            company.campus_website = spec["campus_website"]
            company.work_cities = spec["cities"]
            if _needs_verification_update(company.last_verified_at):
                company.last_verified_at = VERIFIED_AT

            source_name = f"{spec['name']}官方招聘来源"
            source = db.scalar(select(DataSource).where(DataSource.name == source_name))
            if source is None:
                source = DataSource(
                    name=source_name,
                    source_type="curated_official",
                    authorization_note=(
                        "公开官方招聘页面；仅保存求职检索所需摘要和官方跳转链接。"
                        f"核验说明：{spec['evidence']}"
                    ),
                    is_active=True,
                    is_crawl_enabled=False,
                    crawl_interval_minutes=1440,
                    parser_mode="auto",
                    link_keywords=[],
                )
                db.add(source)
            source.base_url = spec["campus_website"]
            source.feed_url = spec["campus_website"]
            source.company_id = company.id
            db.flush()
            company.data_source = source.name
            company.data_source_id = source.id

            for job_spec in spec["jobs"]:
                job = db.scalar(
                    select(Job).where(
                        Job.company_id == company.id,
                        Job.title == job_spec["title"],
                        Job.is_demo.is_(False),
                    )
                )
                if job is None:
                    job = Job(
                        title=job_spec["title"],
                        company_id=company.id,
                        category=job_spec["category"],
                        work_cities=job_spec["cities"],
                        education_requirement=job_spec["education"],
                        major_requirement=job_spec["major"],
                        description=job_spec["description"],
                        requirements="请在提交简历前打开官方页面复核完整任职要求。",
                        application_url=job_spec["application_url"],
                        published_at=_published(job_spec["open_date"]),
                        deadline=_deadline(job_spec.get("deadline")),
                        recruitment_status="open",
                        data_source=source.name,
                        data_source_id=source.id,
                        last_verified_at=VERIFIED_AT,
                        is_demo=False,
                    )
                    db.add(job)
                    created_jobs += 1
                else:
                    job.category = job_spec["category"]
                    job.work_cities = job_spec["cities"]
                    job.education_requirement = job_spec["education"]
                    job.major_requirement = job_spec["major"]
                    job.description = job_spec["description"]
                    job.application_url = job_spec["application_url"]
                    job.published_at = _published(job_spec["open_date"])
                    job.deadline = _deadline(job_spec.get("deadline"))
                    job.data_source = source.name
                    job.data_source_id = source.id
                    if _needs_verification_update(job.last_verified_at):
                        job.last_verified_at = VERIFIED_AT

    print(
        "Official launch seed ready: "
        f"{len(OFFICIAL_COMPANIES)} companies and "
        f"{sum(len(item['jobs']) for item in OFFICIAL_COMPANIES)} jobs "
        f"({created_companies} companies, {created_jobs} jobs created)."
    )


if __name__ == "__main__":
    seed_official()
