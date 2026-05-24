from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator


class OvertimeCreateRequest(BaseModel):
    date: date
    start_time: datetime
    end_time: datetime
    reason: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def validate_times(self) -> "OvertimeCreateRequest":
        if self.end_time <= self.start_time:
            raise ValueError("終了時刻は開始時刻より後にしてください")
        return self


class ReviewRequest(BaseModel):
    comment: str | None = Field(default=None, max_length=500)


class OvertimeRequestResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    user_name: str
    date: date
    start_time: datetime
    end_time: datetime
    minutes: int
    reason: str
    status: str
    reviewer_id: int | None
    reviewer_comment: str | None
    reviewed_at: datetime | None
    created_at: datetime


class OvertimeMonthlySummary(BaseModel):
    user_id: int
    user_name: str
    year: int
    month: int
    total_approved_minutes: int
    alert: bool
