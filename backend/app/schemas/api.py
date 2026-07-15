from datetime import date, datetime
from typing import Generic, Literal, Self, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    pages: int = Field(ge=0)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=100)

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("姓名不能为空")
        return normalized


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    is_admin: bool
    graduation_year: int | None
    education_level: str | None
    target_cities: str | None
    notifications_enabled: bool
    created_at: datetime


class UserUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    graduation_year: int | None = Field(default=None, ge=2024, le=2100)
    education_level: str | None = Field(default=None, max_length=50)
    target_cities: str | None = Field(default=None, max_length=500)
    notifications_enabled: bool | None = None


class DataSourceBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=200)
    source_type: str = Field(default="authorized_csv", max_length=50)
    base_url: str | None = Field(default=None, max_length=500)
    authorization_note: str = Field(min_length=3, max_length=2000)
    license_info: str | None = Field(default=None, max_length=500)
    is_active: bool = True
    company_id: int | None = Field(default=None, gt=0)
    feed_url: str | None = Field(default=None, max_length=1000)
    parser_mode: Literal["auto", "html_links", "rss", "atom", "json_feed"] = "auto"
    link_keywords: list[str] = Field(default_factory=list, max_length=30)
    is_crawl_enabled: bool = False
    crawl_interval_minutes: int = Field(default=360, ge=15, le=10080)

    @field_validator("feed_url")
    @classmethod
    def validate_feed_url(cls, value: str | None) -> str | None:
        if value and not value.lower().startswith(("http://", "https://")):
            raise ValueError("官方招聘源仅支持 HTTP(S) 地址")
        return value

    @model_validator(mode="after")
    def validate_crawl_configuration(self) -> Self:
        if self.is_crawl_enabled and (self.company_id is None or not self.feed_url):
            raise ValueError("启用自动同步前必须选择企业并填写官方招聘源地址")
        return self


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=200)
    source_type: str | None = Field(default=None, max_length=50)
    base_url: str | None = Field(default=None, max_length=500)
    authorization_note: str | None = Field(default=None, min_length=3, max_length=2000)
    license_info: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None
    company_id: int | None = Field(default=None, gt=0)
    feed_url: str | None = Field(default=None, max_length=1000)
    parser_mode: Literal["auto", "html_links", "rss", "atom", "json_feed"] | None = None
    link_keywords: list[str] | None = Field(default=None, max_length=30)
    is_crawl_enabled: bool | None = None
    crawl_interval_minutes: int | None = Field(default=None, ge=15, le=10080)

    @field_validator("feed_url")
    @classmethod
    def validate_feed_url(cls, value: str | None) -> str | None:
        if value and not value.lower().startswith(("http://", "https://")):
            raise ValueError("官方招聘源仅支持 HTTP(S) 地址")
        return value


class DataSourceOut(DataSourceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by: int | None
    last_import_at: datetime | None
    last_crawled_at: datetime | None
    next_crawl_at: datetime | None
    last_crawl_status: str | None
    created_at: datetime
    updated_at: datetime


class CrawlRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int | None
    status: str
    discovered_rows: int
    updated_rows: int
    skipped_rows: int
    error_message: str | None
    started_at: datetime
    finished_at: datetime | None
    created_at: datetime


class ImportBatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int | None
    uploaded_by: int | None
    entity_type: str
    filename: str
    status: str
    total_rows: int
    created_rows: int
    updated_rows: int
    skipped_rows: int
    error_rows: int
    errors: list[dict[str, object]]
    created_at: datetime


class ReviewPayload(BaseModel):
    action: str = Field(pattern="^(approve|reject)$")
    recruitment_status: str = Field(default="open", max_length=50)


class QualitySourceItem(BaseModel):
    source_id: int | None
    source_name: str
    companies: int = Field(ge=0)
    jobs: int = Field(ge=0)


class DataQualityStats(BaseModel):
    companies_total: int = Field(ge=0)
    jobs_total: int = Field(ge=0)
    demo_records: int = Field(ge=0)
    verified_records: int = Field(ge=0)
    unverified_records: int = Field(ge=0)
    stale_records: int = Field(ge=0)
    active_sources: int = Field(ge=0)
    import_batches: int = Field(ge=0)
    source_coverage: list[QualitySourceItem]


class ReviewItem(BaseModel):
    entity_type: str
    id: int
    name: str
    company_name: str | None = None
    source_name: str
    recruitment_status: str
    last_verified_at: datetime | None
    updated_at: datetime


class CompanyBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=200)
    industry: str = Field(min_length=1, max_length=100)
    company_type: str = Field(min_length=1, max_length=100)
    website: str | None = Field(default=None, max_length=500)
    campus_website: str | None = Field(default=None, max_length=500)
    logo_url: str | None = Field(default=None, max_length=500)
    recruitment_status: str = Field(default="unverified", max_length=50)
    open_date: date | None = None
    deadline: date | None = None
    education_requirement: str = Field(min_length=1, max_length=100)
    accepts_college: bool = False
    accepts_bachelor: bool = True
    major_requirement: str | None = None
    work_cities: str = Field(min_length=1, max_length=500)
    data_source: str = Field(default="manual", max_length=200)
    last_verified_at: datetime | None = None
    is_demo: bool = False

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.open_date and self.deadline and self.deadline < self.open_date:
            raise ValueError("截止日期不能早于开放日期")
        return self


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=200)
    industry: str | None = Field(default=None, min_length=1, max_length=100)
    company_type: str | None = Field(default=None, min_length=1, max_length=100)
    website: str | None = Field(default=None, max_length=500)
    campus_website: str | None = Field(default=None, max_length=500)
    logo_url: str | None = Field(default=None, max_length=500)
    recruitment_status: str | None = Field(default=None, min_length=1, max_length=50)
    open_date: date | None = None
    deadline: date | None = None
    education_requirement: str | None = Field(default=None, min_length=1, max_length=100)
    accepts_college: bool | None = None
    accepts_bachelor: bool | None = None
    major_requirement: str | None = None
    work_cities: str | None = Field(default=None, min_length=1, max_length=500)
    data_source: str | None = Field(default=None, min_length=1, max_length=200)
    last_verified_at: datetime | None = None
    is_demo: bool | None = None

    @field_validator(
        "name",
        "industry",
        "company_type",
        "recruitment_status",
        "education_requirement",
        "accepts_college",
        "accepts_bachelor",
        "work_cities",
        "data_source",
        "is_demo",
    )
    @classmethod
    def reject_null_for_required_fields(cls, value: object) -> object:
        if value is None:
            raise ValueError("该字段不能为 null")
        return value


class CompanyOut(CompanyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class JobBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    company_id: int = Field(gt=0)
    category: str = Field(min_length=1, max_length=100)
    work_cities: str = Field(min_length=1, max_length=500)
    education_requirement: str = Field(min_length=1, max_length=100)
    major_requirement: str | None = None
    description: str = Field(min_length=1)
    requirements: str = Field(min_length=1)
    application_url: str | None = Field(default=None, max_length=500)
    published_at: datetime | None = None
    deadline: datetime | None = None
    recruitment_status: str = Field(default="unverified", max_length=50)
    data_source: str = Field(default="manual", max_length=200)
    last_verified_at: datetime | None = None
    is_demo: bool = False

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.published_at and self.deadline and self.deadline < self.published_at:
            raise ValueError("岗位截止时间不能早于发布时间")
        return self


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    company_id: int | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    work_cities: str | None = Field(default=None, min_length=1, max_length=500)
    education_requirement: str | None = Field(default=None, min_length=1, max_length=100)
    major_requirement: str | None = None
    description: str | None = Field(default=None, min_length=1)
    requirements: str | None = Field(default=None, min_length=1)
    application_url: str | None = Field(default=None, max_length=500)
    published_at: datetime | None = None
    deadline: datetime | None = None
    recruitment_status: str | None = Field(default=None, min_length=1, max_length=50)
    data_source: str | None = Field(default=None, min_length=1, max_length=200)
    last_verified_at: datetime | None = None
    is_demo: bool | None = None

    @field_validator(
        "title",
        "company_id",
        "category",
        "work_cities",
        "education_requirement",
        "description",
        "requirements",
        "recruitment_status",
        "data_source",
        "is_demo",
    )
    @classmethod
    def reject_null_for_required_fields(cls, value: object) -> object:
        if value is None:
            raise ValueError("该字段不能为 null")
        return value


class JobOut(JobBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class FavoriteCreate(BaseModel):
    job_id: int = Field(gt=0)


class FavoriteOut(FavoriteCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime


class ApplicationCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    job_id: int = Field(gt=0)
    resume_id: int | None = Field(default=None, gt=0)
    status: str = Field(default="planned", min_length=1, max_length=50)
    applied_at: datetime | None = None
    channel: str | None = Field(default=None, max_length=100)
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    status: str | None = Field(default=None, min_length=1, max_length=50)
    resume_id: int | None = Field(default=None, gt=0)
    applied_at: datetime | None = None
    channel: str | None = Field(default=None, max_length=100)
    notes: str | None = None

    @field_validator("status")
    @classmethod
    def reject_null_status(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("状态不能为 null")
        return value


class ApplicationOut(ApplicationCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class InterviewCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    application_id: int = Field(gt=0)
    interview_type: str = Field(min_length=1, max_length=100)
    scheduled_at: datetime
    status: str = Field(default="scheduled", min_length=1, max_length=50)
    location: str | None = Field(default=None, max_length=300)
    notes: str | None = None


class InterviewUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    interview_type: str | None = Field(default=None, min_length=1, max_length=100)
    scheduled_at: datetime | None = None
    status: str | None = Field(default=None, min_length=1, max_length=50)
    location: str | None = Field(default=None, max_length=300)
    notes: str | None = None

    @field_validator("interview_type", "scheduled_at", "status")
    @classmethod
    def reject_null_for_required_fields(cls, value: object) -> object:
        if value is None:
            raise ValueError("该字段不能为 null")
        return value


class InterviewOut(InterviewCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class OfferCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    application_id: int = Field(gt=0)
    status: str = Field(default="pending", min_length=1, max_length=50)
    compensation: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    received_at: date
    response_deadline: date | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.response_deadline and self.response_deadline < self.received_at:
            raise ValueError("Offer 回复截止日期不能早于收到日期")
        return self


class OfferUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    status: str | None = Field(default=None, min_length=1, max_length=50)
    compensation: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    received_at: date | None = None
    response_deadline: date | None = None
    notes: str | None = None

    @field_validator("status", "received_at")
    @classmethod
    def reject_null_for_required_fields(cls, value: object) -> object:
        if value is None:
            raise ValueError("该字段不能为 null")
        return value

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if (
            self.received_at is not None
            and self.response_deadline is not None
            and self.response_deadline < self.received_at
        ):
            raise ValueError("Offer 回复截止日期不能早于收到日期")
        return self


class OfferOut(OfferCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    notification_type: str
    is_read: bool
    related_entity_type: str | None
    related_entity_id: int | None
    scheduled_for: datetime | None
    created_at: datetime


class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    file_url: str
    version: str | None
    is_default: bool
    original_filename: str
    content_type: str
    file_size: int
    checksum_sha256: str
    created_at: datetime
    updated_at: datetime


class ResumeUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=200)
    version: str | None = Field(default=None, max_length=50)
    is_default: bool | None = None


class JobAlertCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=200)
    criteria: dict[str, object] = Field(default_factory=dict)
    frequency: str = Field(default="daily", pattern="^(daily|weekly|instant)$")
    is_active: bool = True


class JobAlertUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=200)
    criteria: dict[str, object] | None = None
    frequency: str | None = Field(default=None, pattern="^(daily|weekly|instant)$")
    is_active: bool | None = None


class JobAlertOut(JobAlertCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    last_run_at: datetime | None
    next_run_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action: str
    entity_type: str
    entity_id: int | None
    details: dict[str, object] | None
    created_at: datetime


class ReminderRunResult(BaseModel):
    created: int = Field(ge=0)
    job_deadlines: int = Field(ge=0)
    interviews: int = Field(ge=0)
    offers: int = Field(ge=0)


class ApplicationTrendPoint(BaseModel):
    date: date
    count: int = Field(ge=0)


class IndustryDistributionItem(BaseModel):
    industry: str
    count: int = Field(ge=0)


class RecentApplication(BaseModel):
    id: int
    job_id: int
    job_title: str
    company_name: str
    status: str
    applied_at: datetime | None


class DashboardStats(BaseModel):
    open_companies: int = Field(ge=0)
    college_companies: int = Field(ge=0)
    bachelor_companies: int = Field(ge=0)
    new_jobs_today: int = Field(ge=0)
    applications: int = Field(ge=0)
    interviews: int = Field(ge=0)
    offers: int = Field(ge=0)
    expiring_jobs: int = Field(ge=0)
    application_trend: list[ApplicationTrendPoint]
    industry_distribution: list[IndustryDistributionItem]
    recent_applications: list[RecentApplication]
