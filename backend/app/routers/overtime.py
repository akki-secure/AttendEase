from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, get_db, require_manager_or_admin
from app.models.overtime import OvertimeRequest
from app.models.user import User
from app.schemas.overtime import (
    OvertimeCreateRequest,
    OvertimeMonthlySummary,
    OvertimeRequestResponse,
    ReviewRequest,
)

router = APIRouter(prefix="/api/v1/overtime", tags=["overtime"])

MONTHLY_ALERT_MINUTES = 1800  # 30時間


def _to_response(record: OvertimeRequest) -> OvertimeRequestResponse:
    return OvertimeRequestResponse(
        id=record.id,
        user_id=record.user_id,
        user_name=record.user.name,
        date=record.date,
        start_time=record.start_time,
        end_time=record.end_time,
        minutes=record.minutes,
        reason=record.reason,
        status=record.status,
        reviewer_id=record.reviewer_id,
        reviewer_comment=record.reviewer_comment,
        reviewed_at=record.reviewed_at,
        created_at=record.created_at,
    )


async def _get_monthly_approved_minutes(
    db: AsyncSession, user_id: int, year: int, month: int
) -> int:
    result = await db.execute(
        select(func.sum(OvertimeRequest.minutes)).where(
            OvertimeRequest.user_id == user_id,
            OvertimeRequest.status == "APPROVED",
            extract("year", OvertimeRequest.date) == year,
            extract("month", OvertimeRequest.date) == month,
        )
    )
    return result.scalar_one_or_none() or 0


@router.post("", response_model=OvertimeRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_overtime(
    payload: OvertimeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OvertimeRequestResponse:
    start = payload.start_time
    end = payload.end_time
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    minutes = int((end - start).total_seconds() / 60)

    # 同日の重複チェック
    overlap = await db.execute(
        select(OvertimeRequest).where(
            and_(
                OvertimeRequest.user_id == current_user.id,
                OvertimeRequest.status.in_(["PENDING", "APPROVED"]),
                OvertimeRequest.date == payload.date,
            )
        )
    )
    if overlap.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="指定日に既に申請済みの残業申請があります",
        )

    record = OvertimeRequest(
        user_id=current_user.id,
        date=payload.date,
        start_time=start,
        end_time=end,
        minutes=minutes,
        reason=payload.reason,
        status="PENDING",
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)

    result = await db.execute(
        select(OvertimeRequest)
        .options(selectinload(OvertimeRequest.user))
        .where(OvertimeRequest.id == record.id)
    )
    record = result.scalar_one()
    await db.commit()
    return _to_response(record)


@router.get("/me", response_model=list[OvertimeRequestResponse])
async def get_my_overtimes(
    year: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[OvertimeRequestResponse]:
    stmt = (
        select(OvertimeRequest)
        .options(selectinload(OvertimeRequest.user))
        .where(OvertimeRequest.user_id == current_user.id)
        .order_by(OvertimeRequest.created_at.desc())
    )
    if year:
        stmt = stmt.where(extract("year", OvertimeRequest.date) == year)

    result = await db.execute(stmt)
    records = result.scalars().all()
    return [_to_response(r) for r in records]


@router.delete("/{overtime_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_overtime(
    overtime_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(OvertimeRequest).where(OvertimeRequest.id == overtime_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="申請が見つかりません")
    if record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="この申請をキャンセルする権限がありません")
    if record.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="承認待ち以外の申請はキャンセルできません")

    record.status = "CANCELLED"
    await db.commit()


@router.get("/pending", response_model=list[OvertimeRequestResponse])
async def get_pending_overtimes(
    _: User = Depends(require_manager_or_admin),
    db: AsyncSession = Depends(get_db),
) -> list[OvertimeRequestResponse]:
    result = await db.execute(
        select(OvertimeRequest)
        .options(selectinload(OvertimeRequest.user))
        .where(OvertimeRequest.status == "PENDING")
        .order_by(OvertimeRequest.created_at.asc())
    )
    records = result.scalars().all()
    return [_to_response(r) for r in records]


@router.get("/monthly-summary", response_model=list[OvertimeMonthlySummary])
async def get_monthly_summary(
    year: int | None = Query(default=None),
    month: int | None = Query(default=None),
    _: User = Depends(require_manager_or_admin),
    db: AsyncSession = Depends(get_db),
) -> list[OvertimeMonthlySummary]:
    from datetime import date as date_type

    today = date_type.today()
    target_year = year or today.year
    target_month = month or today.month

    users_result = await db.execute(
        select(User).where(User.is_active.is_(True)).order_by(User.name)
    )
    users = users_result.scalars().all()

    summaries = []
    for u in users:
        total = await _get_monthly_approved_minutes(db, u.id, target_year, target_month)
        summaries.append(
            OvertimeMonthlySummary(
                user_id=u.id,
                user_name=u.name,
                year=target_year,
                month=target_month,
                total_approved_minutes=total,
                alert=total >= MONTHLY_ALERT_MINUTES,
            )
        )
    return summaries


@router.post("/{overtime_id}/approve", response_model=OvertimeRequestResponse)
async def approve_overtime(
    overtime_id: int,
    payload: ReviewRequest,
    current_user: User = Depends(require_manager_or_admin),
    db: AsyncSession = Depends(get_db),
) -> OvertimeRequestResponse:
    result = await db.execute(
        select(OvertimeRequest)
        .options(selectinload(OvertimeRequest.user))
        .where(OvertimeRequest.id == overtime_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="申請が見つかりません")
    if record.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="承認待ち以外の申請は操作できません")

    record.status = "APPROVED"
    record.reviewer_id = current_user.id
    record.reviewer_comment = payload.comment
    record.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(record)

    result2 = await db.execute(
        select(OvertimeRequest)
        .options(selectinload(OvertimeRequest.user))
        .where(OvertimeRequest.id == record.id)
    )
    record = result2.scalar_one()
    return _to_response(record)


@router.post("/{overtime_id}/reject", response_model=OvertimeRequestResponse)
async def reject_overtime(
    overtime_id: int,
    payload: ReviewRequest,
    current_user: User = Depends(require_manager_or_admin),
    db: AsyncSession = Depends(get_db),
) -> OvertimeRequestResponse:
    result = await db.execute(
        select(OvertimeRequest)
        .options(selectinload(OvertimeRequest.user))
        .where(OvertimeRequest.id == overtime_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="申請が見つかりません")
    if record.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="承認待ち以外の申請は操作できません")

    record.status = "REJECTED"
    record.reviewer_id = current_user.id
    record.reviewer_comment = payload.comment
    record.reviewed_at = datetime.now(timezone.utc)
    await db.commit()

    result2 = await db.execute(
        select(OvertimeRequest)
        .options(selectinload(OvertimeRequest.user))
        .where(OvertimeRequest.id == record.id)
    )
    record = result2.scalar_one()
    return _to_response(record)
