from datetime import date, datetime, time
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)


class ServiceBase(StrictModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str = Field(default="", max_length=10000)
    price: int = Field(..., ge=0)
    duration_minutes: int = Field(..., gt=0)
    is_active: bool = True


class ServiceOut(ServiceBase):
    id: int
    created_at: datetime
    updated_at: datetime


class DoctorBase(StrictModel):
    full_name: str = Field(..., min_length=1, max_length=160)
    specialty: str = Field(..., min_length=1, max_length=120)
    bio: str = Field(default="", max_length=10000)
    photo_url: str | None = Field(default=None, max_length=500)
    experience_years: int = Field(default=0, ge=0)
    work_start: time = time(9, 0)
    work_end: time = time(18, 0)
    slot_minutes: int = Field(default=30, gt=0)
    is_active: bool = True
    service_ids: list[int]

    @model_validator(mode="after")
    def valid_schedule(self):
        if self.work_end <= self.work_start:
            raise ValueError("work_end must be later than work_start")
        if not self.service_ids or len(self.service_ids) != len(set(self.service_ids)):
            raise ValueError("service_ids must contain at least one unique service")
        return self


class DoctorOut(StrictModel):
    id: int
    full_name: str
    specialty: str
    bio: str
    photo_url: str | None
    experience_years: int
    work_start: time
    work_end: time
    slot_minutes: int
    is_active: bool
    service_ids: list[int]
    created_at: datetime
    updated_at: datetime


class FaqBase(StrictModel):
    question: str = Field(..., min_length=1, max_length=500)
    answer: str = Field(..., min_length=1)
    sort_order: int = 0
    is_active: bool = True


class FaqOut(FaqBase):
    id: int
    created_at: datetime
    updated_at: datetime


class AppointmentStatus(str, Enum):
    new = "new"
    confirmed = "confirmed"
    cancelled = "cancelled"


class AppointmentCreate(StrictModel):
    doctor_id: int
    service_id: int
    slot_start: datetime
    client_name: str = Field(..., min_length=1, max_length=120)
    client_phone: str = Field(..., min_length=5, max_length=32)
    utm_source: str | None = Field(default=None, max_length=255)
    utm_medium: str | None = Field(default=None, max_length=255)
    utm_campaign: str | None = Field(default=None, max_length=255)
    utm_content: str | None = Field(default=None, max_length=255)
    utm_term: str | None = Field(default=None, max_length=255)
    source: str | None = Field(default=None, max_length=255)
    client_id: str | None = Field(default=None, max_length=255)

    @field_validator("slot_start")
    @classmethod
    def naive_datetime(cls, value: datetime):
        if value.tzinfo is not None:
            raise ValueError("slot_start must be timezone-naive")
        if value.microsecond:
            raise ValueError("slot_start must use whole seconds")
        return value

    @field_validator("client_phone")
    @classmethod
    def normalize_phone(cls, value: str):
        value = value.strip()
        if any(not (ch.isascii() and ch.isdigit()) and ch not in "+-() " for ch in value):
            raise ValueError("invalid phone")
        if value.count("+") > 1 or ("+" in value and not value.startswith("+")):
            raise ValueError("invalid phone")
        digits = "".join(ch for ch in value if ch.isascii() and ch.isdigit())
        if not 10 <= len(digits) <= 15:
            raise ValueError("invalid phone")
        return f"+{digits}" if value.startswith("+") else digits


class AppointmentOut(StrictModel):
    id: int
    doctor_id: int
    service_id: int
    slot_start: datetime
    client_name: str
    client_phone: str
    status: AppointmentStatus
    utm_source: str | None
    utm_medium: str | None
    utm_campaign: str | None
    utm_content: str | None
    utm_term: str | None
    source: str | None
    client_id: str | None
    lead_id: UUID
    created_at: datetime
    updated_at: datetime


class AppointmentStatusUpdate(StrictModel):
    status: AppointmentStatus


class LoginRequest(StrictModel):
    username: str = Field(..., min_length=1, max_length=80)
    password: str = Field(..., min_length=1)


class SeoUpdate(StrictModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=500)


class SeoOut(SeoUpdate):
    page: str


class StatusError(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: StatusError
