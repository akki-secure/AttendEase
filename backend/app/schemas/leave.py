from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, Field, model_validator

TIME_BASED_LEAVE_TYPES = ("LATE", "EARLY_LEAVE")


class LeaveCreateRequest(BaseModel):
    leave_type: Literal["ANNUAL", "SPECIAL", "LATE", "EARLY_LEAVE"]
    start_date: date
    end_date: date
    reason: str = Field(min_length=1, max_length=500)
    scheduled_time: time | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "LeaveCreateRequest":
        if self.start_date > self.end_date:
            raise ValueError("終了日は開始日以降を指定してください")
        if self.leave_type in TIME_BASED_LEAVE_TYPES:
            if self.start_date != self.end_date:
                raise ValueError("遅刻・早退は単日のみ申請できます")
            if self.scheduled_time is None:
                raise ValueError("本来の予定時刻を入力してください")
        elif self.scheduled_time is not None:
            raise ValueError("この休暇種別では予定時刻は指定できません")
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
    scheduled_time: time | None
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
