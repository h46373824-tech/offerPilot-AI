from datetime import date, datetime
from typing import Generic, Self, TypeVar

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
    created_at: datetime


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
    status: str = Field(default="planned", min_length=1, max_length=50)
    applied_at: datetime | None = None
    channel: str | None = Field(default=None, max_length=100)
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    status: str | None = Field(default=None, min_length=1, max_length=50)
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
    created_at: datetime


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
