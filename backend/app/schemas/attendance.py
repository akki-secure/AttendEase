from datetime import date, datetime

from pydantic import BaseModel, Field


class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    date: date
    clock_in: datetime | None
    clock_out: datetime | None
    break_minutes: int
    status: str
    correction_note: str | None
    work_minutes: int | None  # clock_out - clock_in - break_minutes（退勤後のみ）

    model_config = {"from_attributes": True}


class TodayStatusResponse(BaseModel):
    date: date
    status: str  # NOT_CLOCKED_IN / PRESENT / CLOSED / CORRECTION_PENDING / CORRECTION_APPROVED
    record: AttendanceResponse | None


class ClockInRequest(BaseModel):
    clock_in: datetime | None = None  # None のときサーバー現在時刻を使用


class ClockOutRequest(BaseModel):
    clock_out: datetime | None = None  # None のときサーバー現在時刻を使用


class FixClockInRequest(BaseModel):
    clock_in: datetime


class FixClockOutRequest(BaseModel):
    clock_out: datetime


class CorrectionRequest(BaseModel):
    clock_in: datetime
    clock_out: datetime
    break_minutes: int = Field(ge=0, default=0)
    note: str = Field(min_length=1, max_length=500)


class MonthlyAttendanceResponse(BaseModel):
    month: str  # "2026-05"
    records: list[AttendanceResponse]
    total_work_minutes: int
    total_overtime_minutes: int  # 所定 480 分超


class MonthlySummaryItem(BaseModel):
    month: str       # "2026-01"
    work_minutes: int
    overtime_minutes: int


class YearlySummaryResponse(BaseModel):
    year: int
    months: list[MonthlySummaryItem]
    total_work_minutes: int
    total_overtime_minutes: int
