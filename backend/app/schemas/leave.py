from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class LeaveCreateRequest(BaseModel):
    leave_type: Literal["ANNUAL", "SPECIAL"]
    start_date: date
    end_date: date
    reason: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def validate_dates(self) -> "LeaveCreateRequest":
        if self.start_date > self.end_date:
            raise ValueError("終了日は開始日以降を指定してください")
        return self


class ReviewRequest(BaseModel):
    comment: str | None = Field(default=None, max_length=500)


class LeaveRequestResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    user_name: str
    leave_type: str
    start_date: date
    end_date: date
    days: int
    reason: str
    status: str
    reviewer_id: int | None
    reviewer_comment: str | None
    reviewed_at: datetime | None
    created_at: datetime


class LeaveBalanceResponse(BaseModel):
    model_config = {"from_attributes": True}

    user_id: int
    user_name: str
    year: int
    granted_days: int
    used_days: int
    remaining_days: int


class LeaveBalanceUpdateRequest(BaseModel):
    granted_days: int = Field(ge=0)
