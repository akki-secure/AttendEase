import asyncio
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

_JST = ZoneInfo("Asia/Tokyo")

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, extract, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.background import send_emails_background
from app.core.deps import get_current_user, get_db, require_manager_or_admin
from app.core.email import send_correction_request_email, send_correction_reviewed_email
from app.core.time import legal_break_minutes, round_down_overtime_minutes
from app.models.attendance import AttendanceRecord
from app.models.notification import Notification
from app.models.user import User
from app.schemas.attendance import (
    AttendanceResponse,
    ClockInRequest,
    ClockOutRequest,
    CorrectionRequest,
    CorrectionRequestResponse,
    CorrectionReviewRequest,
    FixClockInRequest,
    FixClockOutRequest,
    MonthlyAttendanceResponse,
    MonthlySummaryItem,
    PastRecordRequest,
    TodayStatusResponse,
    YearlySummaryResponse,
)

router = APIRouter()

_STANDARD_WORK_MINUTES = 480  # 8 時間


def _ensure_utc(dt: datetime | None) -> datetime | None:
    """Naive datetimes from SQLite are UTC – attach tzinfo so Pydantic serializes with offset."""
    if dt is None:
        return None
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def _to_response(record: AttendanceRecord) -> AttendanceResponse:
    clock_in = _ensure_utc(record.clock_in)
    clock_out = _ensure_utc(record.clock_out)

    work_minutes: int | None = None
    if clock_in and clock_out:
        delta = int((clock_out - clock_in).total_seconds() // 60)
        work_minutes = max(delta - record.break_minutes, 0)

    return AttendanceResponse(
        id=record.id,
        user_id=record.user_id,
        date=record.date,
        clock_in=clock_in,
        clock_out=clock_out,
        break_minutes=record.break_minutes,
        status=record.status,
        work_type=record.work_type,
        correction_note=record.correction_note,
        work_minutes=work_minutes,
        reviewer_id=record.reviewer_id,
        reviewer_comment=record.reviewer_comment,
        reviewed_at=_ensure_utc(record.reviewed_at),
    )


def _to_correction_response(record: AttendanceRecord) -> CorrectionRequestResponse:
    base = _to_response(record)
    return CorrectionRequestResponse(user_name=record.user.name, **base.model_dump())


async def _get_today_record(
    db: AsyncSession, user_id: int, today: date
) -> AttendanceRecord | None:
    result = await db.execute(
        select(AttendanceRecord).where(
            and_(AttendanceRecord.user_id == user_id, AttendanceRecord.date == today)
        )
    )
    return result.scalar_one_or_none()


@router.get("/today", response_model=TodayStatusResponse)
async def get_today_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TodayStatusResponse:
    today = datetime.now(_JST).date()
    record = await _get_today_record(db, current_user.id, today)

    if record is None:
        return TodayStatusResponse(date=today, status="NOT_CLOCKED_IN", record=None)

    return TodayStatusResponse(date=today, status=record.status, record=_to_response(record))


@router.post("/clock-in", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def clock_in(
    payload: ClockInRequest = ClockInRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AttendanceResponse:
    now = datetime.now(timezone.utc)
    clock_in_dt = payload.clock_in if payload.clock_in is not None else now
    if clock_in_dt.tzinfo is None:
        clock_in_dt = clock_in_dt.replace(tzinfo=timezone.utc)
    today = datetime.now(_JST).date()

    existing = await _get_today_record(db, current_user.id, today)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="本日はすでに出勤打刻済みです",
        )

    record = AttendanceRecord(
        user_id=current_user.id,
        date=today,
        clock_in=clock_in_dt,
        work_type=payload.work_type,
        status="PRESENT",
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return _to_response(record)


@router.post("/clock-out", response_model=AttendanceResponse)
async def clock_out(
    payload: ClockOutRequest = ClockOutRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AttendanceResponse:
    now = datetime.now(timezone.utc)
    clock_out_dt = payload.clock_out if payload.clock_out is not None else now
    if clock_out_dt.tzinfo is None:
        clock_out_dt = clock_out_dt.replace(tzinfo=timezone.utc)
    today = now.date()

    record = await _get_today_record(db, current_user.id, today)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="本日の出勤打刻が見つかりません",
        )
    if record.status == "CLOSED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="本日はすでに退勤打刻済みです",
        )
    if record.status != "PRESENT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="現在の状態では退勤打刻できません",
        )
    if record.clock_in and clock_out_dt < _ensure_utc(record.clock_in):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="退勤時刻は出勤時刻より後にしてください",
        )

    total_minutes = int((clock_out_dt - _ensure_utc(record.clock_in)).total_seconds() // 60)
    record.clock_out = clock_out_dt
    record.break_minutes = legal_break_minutes(total_minutes)
    record.status = "CLOSED"
    await db.commit()
    await db.refresh(record)
    return _to_response(record)


@router.patch("/today/clock-in", response_model=AttendanceResponse)
async def fix_today_clock_in(
    payload: FixClockInRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AttendanceResponse:
    """出勤中のみ: 本日の出勤時刻を直接修正する（承認不要）"""
    today = datetime.now(_JST).date()
    record = await _get_today_record(db, current_user.id, today)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="本日の打刻記録が見つかりません")
    if record.status not in ("PRESENT", "CLOSED"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="出勤中または退勤済みのみ出勤時刻を修正できます")

    clock_in_dt = payload.clock_in
    if clock_in_dt.tzinfo is None:
        clock_in_dt = clock_in_dt.replace(tzinfo=timezone.utc)

    if record.clock_out and clock_in_dt >= _ensure_utc(record.clock_out):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="出勤時刻は退勤時刻より前にしてください",
        )

    record.clock_in = clock_in_dt
    if "work_type" in payload.model_fields_set:
        record.work_type = payload.work_type
    if record.clock_out:
        total_minutes = int((_ensure_utc(record.clock_out) - clock_in_dt).total_seconds() // 60)
        record.break_minutes = legal_break_minutes(total_minutes)
    await db.commit()
    await db.refresh(record)
    return _to_response(record)


@router.patch("/today/clock-out", response_model=AttendanceResponse)
async def fix_today_clock_out(
    payload: FixClockOutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AttendanceResponse:
    """退勤済みのみ: 本日の退勤時刻を直接修正する（当日のみ承認不要）"""
    today = datetime.now(_JST).date()
    record = await _get_today_record(db, current_user.id, today)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="本日の打刻記録が見つかりません")
    if record.status != "CLOSED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="退勤済みのみ退勤時刻を修正できます")

    clock_out_dt = payload.clock_out
    if clock_out_dt.tzinfo is None:
        clock_out_dt = clock_out_dt.replace(tzinfo=timezone.utc)
    if record.clock_in and clock_out_dt < _ensure_utc(record.clock_in):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="退勤時刻は出勤時刻より後にしてください",
        )

    total_minutes = int((clock_out_dt - _ensure_utc(record.clock_in)).total_seconds() // 60)
    record.clock_out = clock_out_dt
    record.break_minutes = legal_break_minutes(total_minutes)
    await db.commit()
    await db.refresh(record)
    return _to_response(record)


@router.post("/record", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def create_past_record(
    payload: PastRecordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AttendanceResponse:
    """当月の過去日付の打刻を直接登録する（承認不要）"""
    today_jst = datetime.now(_JST).date()

    if payload.date >= today_jst:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="過去の日付のみ登録できます",
        )

    first_of_month = today_jst.replace(day=1)
    if payload.date < first_of_month:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="当月の日付のみ登録できます",
        )

    clock_in_dt = payload.clock_in
    if clock_in_dt.tzinfo is None:
        clock_in_dt = clock_in_dt.replace(tzinfo=timezone.utc)
    clock_out_dt = payload.clock_out
    if clock_out_dt.tzinfo is None:
        clock_out_dt = clock_out_dt.replace(tzinfo=timezone.utc)

    if clock_in_dt.astimezone(_JST).date() != payload.date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="出勤時刻は指定日と同じ日付にしてください",
        )

    if clock_out_dt.astimezone(_JST).date() > payload.date + timedelta(days=1):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="退勤時刻は翌日までにしてください",
        )

    if clock_out_dt <= clock_in_dt:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="退勤時刻は出勤時刻より後にしてください",
        )

    existing = await _get_today_record(db, current_user.id, payload.date)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="指定日の打刻記録はすでに存在します",
        )

    record = AttendanceRecord(
        user_id=current_user.id,
        date=payload.date,
        clock_in=clock_in_dt,
        clock_out=clock_out_dt,
        break_minutes=payload.break_minutes,
        work_type=payload.work_type,
        status="CLOSED",
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return _to_response(record)


@router.get("/me", response_model=MonthlyAttendanceResponse)
async def get_my_monthly(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$", description="例: 2026-05"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MonthlyAttendanceResponse:
    year, mon = int(month[:4]), int(month[5:7])

    result = await db.execute(
        select(AttendanceRecord).where(
            and_(
                AttendanceRecord.user_id == current_user.id,
                extract("year", AttendanceRecord.date) == year,
                extract("month", AttendanceRecord.date) == mon,
            )
        ).order_by(AttendanceRecord.date)
    )
    records = result.scalars().all()
    responses = [_to_response(r) for r in records]

    total_work = 0
    total_overtime = 0
    for r in responses:
        w = r.work_minutes or 0
        total_work += w
        total_overtime += round_down_overtime_minutes(max(w - _STANDARD_WORK_MINUTES, 0))

    return MonthlyAttendanceResponse(
        month=month,
        records=responses,
        total_work_minutes=total_work,
        total_overtime_minutes=total_overtime,
    )


@router.get("/me/yearly", response_model=YearlySummaryResponse)
async def get_my_yearly(
    year: int = Query(..., description="年（例: 2026）"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> YearlySummaryResponse:
    result = await db.execute(
        select(AttendanceRecord).where(
            and_(
                AttendanceRecord.user_id == current_user.id,
                extract("year", AttendanceRecord.date) == year,
            )
        ).order_by(AttendanceRecord.date)
    )
    records = result.scalars().all()

    monthly: dict[str, MonthlySummaryItem] = {}
    for mon in range(1, 13):
        key = f"{year}-{mon:02d}"
        monthly[key] = MonthlySummaryItem(month=key, work_minutes=0, overtime_minutes=0)

    for rec in records:
        key = f"{year}-{rec.date.month:02d}"
        if rec.clock_in and rec.clock_out:
            ci = _ensure_utc(rec.clock_in)
            co = _ensure_utc(rec.clock_out)
            if ci and co:
                work = max(int((co - ci).total_seconds() // 60) - rec.break_minutes, 0)
                ot = round_down_overtime_minutes(max(work - _STANDARD_WORK_MINUTES, 0))
                monthly[key].work_minutes += work
                monthly[key].overtime_minutes += ot

    months = list(monthly.values())
    total_work = sum(m.work_minutes for m in months)
    total_ot = sum(m.overtime_minutes for m in months)
    return YearlySummaryResponse(year=year, months=months, total_work_minutes=total_work, total_overtime_minutes=total_ot)


@router.patch("/{record_id}/correction-request", response_model=AttendanceResponse)
async def request_correction(
    record_id: int,
    payload: CorrectionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AttendanceResponse:
    result = await db.execute(
        select(AttendanceRecord)
        .options(selectinload(AttendanceRecord.user))
        .where(and_(AttendanceRecord.id == record_id, AttendanceRecord.user_id == current_user.id))
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="打刻記録が見つかりません")

    clock_in = payload.clock_in
    clock_out = payload.clock_out
    if clock_out == clock_in:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="退勤時刻は出勤時刻より後にしてください",
        )
    if clock_out < clock_in:
        # 退勤時刻が出勤時刻より前 = 日をまたぐ勤務（夜勤）とみなし翌日として扱う
        clock_out = clock_out + timedelta(days=1)

    if record.status != "CORRECTION_PENDING":
        record.original_clock_in = record.clock_in
        record.original_clock_out = record.clock_out
        record.original_break_minutes = record.break_minutes
        record.original_status = record.status

    record.clock_in = clock_in
    record.clock_out = clock_out
    record.break_minutes = payload.break_minutes
    record.correction_note = payload.note
    record.status = "CORRECTION_PENDING"
    record.reviewer_id = None
    record.reviewer_comment = None
    record.reviewed_at = None
    await db.commit()
    await db.refresh(record)

    date_str = record.date.strftime("%Y/%m/%d")
    message = f"{current_user.name} さんから勤怠修正申請が届きました（{date_str}）"
    managers_result = await db.execute(
        select(User).where(User.role.in_(["MANAGER", "ADMIN"]), User.is_active.is_(True))
    )
    managers = managers_result.scalars().all()
    email_tasks = []
    for m in managers:
        db.add(Notification(user_id=m.id, type="CORRECTION_REQUEST", message=message))
        if m.email:
            email_tasks.append((send_correction_request_email, (m.email, current_user.name, date_str)))

    await db.commit()
    asyncio.get_event_loop().run_in_executor(None, send_emails_background, email_tasks)

    return _to_response(record)


@router.get("/corrections/pending", response_model=list[CorrectionRequestResponse])
async def get_pending_corrections(
    _: User = Depends(require_manager_or_admin),
    db: AsyncSession = Depends(get_db),
) -> list[CorrectionRequestResponse]:
    result = await db.execute(
        select(AttendanceRecord)
        .options(selectinload(AttendanceRecord.user))
        .where(AttendanceRecord.status == "CORRECTION_PENDING")
        .order_by(AttendanceRecord.updated_at.asc())
    )
    records = result.scalars().all()
    return [_to_correction_response(r) for r in records]


@router.post("/corrections/{record_id}/approve", response_model=CorrectionRequestResponse)
async def approve_correction(
    record_id: int,
    payload: CorrectionReviewRequest,
    current_user: User = Depends(require_manager_or_admin),
    db: AsyncSession = Depends(get_db),
) -> CorrectionRequestResponse:
    result = await db.execute(
        select(AttendanceRecord)
        .options(selectinload(AttendanceRecord.user))
        .where(AttendanceRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="打刻記録が見つかりません")
    if record.status != "CORRECTION_PENDING":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="承認待ち以外の申請は操作できません")

    record.status = "CORRECTION_APPROVED"
    record.reviewer_id = current_user.id
    record.reviewer_comment = payload.comment
    record.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(record)

    date_str = record.date.strftime("%Y/%m/%d")
    message = f"勤怠修正申請（{date_str}）が承認されました"
    db.add(Notification(user_id=record.user_id, type="CORRECTION_APPROVED", message=message))
    await db.commit()

    if record.user.email:
        asyncio.get_event_loop().run_in_executor(
            None,
            send_emails_background,
            [(send_correction_reviewed_email, (record.user.email, record.user.name, "APPROVED", payload.comment, date_str))],
        )

    return _to_correction_response(record)


@router.post("/corrections/{record_id}/reject", response_model=CorrectionRequestResponse)
async def reject_correction(
    record_id: int,
    payload: CorrectionReviewRequest,
    current_user: User = Depends(require_manager_or_admin),
    db: AsyncSession = Depends(get_db),
) -> CorrectionRequestResponse:
    result = await db.execute(
        select(AttendanceRecord)
        .options(selectinload(AttendanceRecord.user))
        .where(AttendanceRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="打刻記録が見つかりません")
    if record.status != "CORRECTION_PENDING":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="承認待ち以外の申請は操作できません")

    record.clock_in = record.original_clock_in
    record.clock_out = record.original_clock_out
    record.break_minutes = record.original_break_minutes or 0
    record.status = record.original_status or ("CLOSED" if record.clock_out else "PRESENT")
    record.original_clock_in = None
    record.original_clock_out = None
    record.original_break_minutes = None
    record.original_status = None
    record.reviewer_id = current_user.id
    record.reviewer_comment = payload.comment
    record.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(record)

    date_str = record.date.strftime("%Y/%m/%d")
    message = f"勤怠修正申請（{date_str}）が否認されました"
    if payload.comment:
        message += f"：{payload.comment}"
    db.add(Notification(user_id=record.user_id, type="CORRECTION_REJECTED", message=message))
    await db.commit()

    if record.user.email:
        asyncio.get_event_loop().run_in_executor(
            None,
            send_emails_background,
            [(send_correction_reviewed_email, (record.user.email, record.user.name, "REJECTED", payload.comment, date_str))],
        )

    return _to_correction_response(record)
