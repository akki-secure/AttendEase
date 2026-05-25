import csv
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import and_, extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_manager_or_admin
from app.models.attendance import AttendanceRecord
from app.models.leave import LeaveRequest
from app.models.overtime import OvertimeRequest
from app.models.user import User

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])

_STANDARD_WORK_MINUTES = 480

_STATUS_LABEL = {
    "PENDING": "申請中",
    "APPROVED": "承認済",
    "REJECTED": "却下",
    "CANCELLED": "取消",
}

_ATTENDANCE_STATUS_LABEL = {
    "PRESENT": "出勤中",
    "CLOSED": "退勤済",
    "CORRECTION_PENDING": "修正申請中",
    "CORRECTION_APPROVED": "修正承認済",
}

_LEAVE_TYPE_LABEL = {"ANNUAL": "有給休暇", "SPECIAL": "特別休暇"}


def _ensure_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def _fmt_dt(dt: datetime | None) -> str:
    dt = _ensure_utc(dt)
    return dt.strftime("%Y-%m-%d %H:%M") if dt else ""


def _minutes_to_hm(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    return f"{h}:{m:02d}"


def _csv_response(output: io.StringIO, filename: str) -> StreamingResponse:
    content = "﻿" + output.getvalue()  # BOM for Excel
    return StreamingResponse(
        iter([content]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ── Schemas ────────────────────────────────────────────────────────────────


class UserMonthlySummary(BaseModel):
    user_id: int
    employee_id: str
    name: str
    work_days: int
    total_work_minutes: int
    total_overtime_minutes: int
    leave_days: int


class MonthlySummaryResponse(BaseModel):
    month: str
    users: list[UserMonthlySummary]
    total_work_minutes: int
    total_overtime_minutes: int


# ── Endpoints ──────────────────────────────────────────────────────────────


@router.get("/summary", response_model=MonthlySummaryResponse)
async def get_monthly_summary(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$", description="例: 2026-05"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_manager_or_admin),
) -> MonthlySummaryResponse:
    year, mon = int(month[:4]), int(month[5:7])

    users_result = await db.execute(select(User).where(User.is_active.is_(True)).order_by(User.name))
    users = users_result.scalars().all()

    att_result = await db.execute(
        select(AttendanceRecord).where(
            and_(
                extract("year", AttendanceRecord.date) == year,
                extract("month", AttendanceRecord.date) == mon,
            )
        )
    )
    att_by_user: dict[int, list[AttendanceRecord]] = {}
    for r in att_result.scalars().all():
        att_by_user.setdefault(r.user_id, []).append(r)

    leave_result = await db.execute(
        select(LeaveRequest).where(
            and_(
                LeaveRequest.status == "APPROVED",
                extract("year", LeaveRequest.start_date) == year,
                extract("month", LeaveRequest.start_date) == mon,
            )
        )
    )
    leave_days_by_user: dict[int, int] = {}
    for lr in leave_result.scalars().all():
        leave_days_by_user[lr.user_id] = leave_days_by_user.get(lr.user_id, 0) + lr.days

    summaries: list[UserMonthlySummary] = []
    for u in users:
        recs = att_by_user.get(u.id, [])
        work_days = sum(1 for r in recs if r.clock_in is not None)
        total_work = 0
        total_ot = 0
        for r in recs:
            if r.clock_in and r.clock_out:
                ci = _ensure_utc(r.clock_in)
                co = _ensure_utc(r.clock_out)
                if ci and co:
                    w = max(int((co - ci).total_seconds() // 60) - r.break_minutes, 0)
                    total_work += w
                    total_ot += max(w - _STANDARD_WORK_MINUTES, 0)
        summaries.append(UserMonthlySummary(
            user_id=u.id,
            employee_id=u.employee_id,
            name=u.name,
            work_days=work_days,
            total_work_minutes=total_work,
            total_overtime_minutes=total_ot,
            leave_days=leave_days_by_user.get(u.id, 0),
        ))

    return MonthlySummaryResponse(
        month=month,
        users=summaries,
        total_work_minutes=sum(s.total_work_minutes for s in summaries),
        total_overtime_minutes=sum(s.total_overtime_minutes for s in summaries),
    )


@router.get("/attendance/csv")
async def download_attendance_csv(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_manager_or_admin),
) -> StreamingResponse:
    year, mon = int(month[:4]), int(month[5:7])

    users_result = await db.execute(select(User))
    users = {u.id: u for u in users_result.scalars().all()}

    att_result = await db.execute(
        select(AttendanceRecord).where(
            and_(
                extract("year", AttendanceRecord.date) == year,
                extract("month", AttendanceRecord.date) == mon,
            )
        ).order_by(AttendanceRecord.user_id, AttendanceRecord.date)
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["社員ID", "氏名", "日付", "出勤時刻", "退勤時刻", "休憩(分)", "実働時間", "残業時間", "ステータス", "修正メモ"])

    for r in att_result.scalars().all():
        u = users.get(r.user_id)
        work = 0
        ot = 0
        if r.clock_in and r.clock_out:
            ci = _ensure_utc(r.clock_in)
            co = _ensure_utc(r.clock_out)
            if ci and co:
                work = max(int((co - ci).total_seconds() // 60) - r.break_minutes, 0)
                ot = max(work - _STANDARD_WORK_MINUTES, 0)
        writer.writerow([
            u.employee_id if u else "",
            u.name if u else "",
            r.date.strftime("%Y-%m-%d"),
            _fmt_dt(r.clock_in),
            _fmt_dt(r.clock_out),
            r.break_minutes,
            _minutes_to_hm(work),
            _minutes_to_hm(ot),
            _ATTENDANCE_STATUS_LABEL.get(r.status, r.status),
            r.correction_note or "",
        ])

    output.seek(0)
    return _csv_response(output, f"attendance_{month}.csv")


@router.get("/leaves/csv")
async def download_leaves_csv(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_manager_or_admin),
) -> StreamingResponse:
    year, mon = int(month[:4]), int(month[5:7])

    users_result = await db.execute(select(User))
    users = {u.id: u for u in users_result.scalars().all()}

    leaves_result = await db.execute(
        select(LeaveRequest).where(
            and_(
                extract("year", LeaveRequest.start_date) == year,
                extract("month", LeaveRequest.start_date) == mon,
            )
        ).order_by(LeaveRequest.user_id, LeaveRequest.start_date)
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["社員ID", "氏名", "休暇種別", "開始日", "終了日", "日数", "理由", "ステータス", "審査者", "審査日", "審査コメント"])

    for lr in leaves_result.scalars().all():
        u = users.get(lr.user_id)
        reviewer = users.get(lr.reviewer_id) if lr.reviewer_id else None
        writer.writerow([
            u.employee_id if u else "",
            u.name if u else "",
            _LEAVE_TYPE_LABEL.get(lr.leave_type, lr.leave_type),
            lr.start_date.strftime("%Y-%m-%d"),
            lr.end_date.strftime("%Y-%m-%d"),
            lr.days,
            lr.reason,
            _STATUS_LABEL.get(lr.status, lr.status),
            reviewer.name if reviewer else "",
            _fmt_dt(lr.reviewed_at),
            lr.reviewer_comment or "",
        ])

    output.seek(0)
    return _csv_response(output, f"leaves_{month}.csv")


@router.get("/overtime/csv")
async def download_overtime_csv(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_manager_or_admin),
) -> StreamingResponse:
    year, mon = int(month[:4]), int(month[5:7])

    users_result = await db.execute(select(User))
    users = {u.id: u for u in users_result.scalars().all()}

    ot_result = await db.execute(
        select(OvertimeRequest).where(
            and_(
                extract("year", OvertimeRequest.date) == year,
                extract("month", OvertimeRequest.date) == mon,
            )
        ).order_by(OvertimeRequest.user_id, OvertimeRequest.date)
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["社員ID", "氏名", "残業日", "開始時刻", "終了時刻", "残業時間", "理由", "ステータス", "審査者", "審査日", "審査コメント"])

    for ot in ot_result.scalars().all():
        u = users.get(ot.user_id)
        reviewer = users.get(ot.reviewer_id) if ot.reviewer_id else None
        writer.writerow([
            u.employee_id if u else "",
            u.name if u else "",
            ot.date.strftime("%Y-%m-%d"),
            _fmt_dt(ot.start_time),
            _fmt_dt(ot.end_time),
            _minutes_to_hm(ot.minutes),
            ot.reason,
            _STATUS_LABEL.get(ot.status, ot.status),
            reviewer.name if reviewer else "",
            _fmt_dt(ot.reviewed_at),
            ot.reviewer_comment or "",
        ])

    output.seek(0)
    return _csv_response(output, f"overtime_{month}.csv")
