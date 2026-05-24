from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, get_db, require_manager_or_admin
from app.models.leave import LeaveRequest
from app.models.leave_balance import LeaveBalance
from app.models.user import User
from app.schemas.leave import (
    LeaveBalanceResponse,
    LeaveCreateRequest,
    LeaveRequestResponse,
    ReviewRequest,
)

router = APIRouter(prefix="/api/v1/leaves", tags=["leaves"])


def _to_response(record: LeaveRequest) -> LeaveRequestResponse:
    return LeaveRequestResponse(
        id=record.id,
        user_id=record.user_id,
        user_name=record.user.name,
        leave_type=record.leave_type,
        start_date=record.start_date,
        end_date=record.end_date,
        days=record.days,
        reason=record.reason,
        status=record.status,
        reviewer_id=record.reviewer_id,
        reviewer_comment=record.reviewer_comment,
        reviewed_at=record.reviewed_at,
        created_at=record.created_at,
    )


async def _get_balance(db: AsyncSession, user_id: int, year: int) -> LeaveBalance | None:
    result = await db.execute(
        select(LeaveBalance).where(LeaveBalance.user_id == user_id, LeaveBalance.year == year)
    )
    return result.scalar_one_or_none()


@router.post("", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_leave(
    payload: LeaveCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeaveRequestResponse:
    days = (payload.end_date - payload.start_date).days + 1

    # 重複チェック
    overlap = await db.execute(
        select(LeaveRequest).where(
            and_(
                LeaveRequest.user_id == current_user.id,
                LeaveRequest.status.in_(["PENDING", "APPROVED"]),
                LeaveRequest.start_date <= payload.end_date,
                LeaveRequest.end_date >= payload.start_date,
            )
        )
    )
    if overlap.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="指定期間に既に申請済みの休暇があります",
        )

    # 有給残日数チェック
    if payload.leave_type == "ANNUAL":
        year = payload.start_date.year
        balance = await _get_balance(db, current_user.id, year)
        remaining = (balance.granted_days - balance.used_days) if balance else 0
        if remaining < days:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"有給残日数が不足しています（残{remaining}日、申請{days}日）",
            )

    record = LeaveRequest(
        user_id=current_user.id,
        leave_type=payload.leave_type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        days=days,
        reason=payload.reason,
        status="PENDING",
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)

    result = await db.execute(
        select(LeaveRequest)
        .options(selectinload(LeaveRequest.user))
        .where(LeaveRequest.id == record.id)
    )
    record = result.scalar_one()
    await db.commit()
    return _to_response(record)


@router.get("/my-balance", response_model=LeaveBalanceResponse)
async def get_my_balance(
    year: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeaveBalanceResponse:
    from datetime import date as date_type

    target_year = year or date_type.today().year
    balance = await _get_balance(db, current_user.id, target_year)
    granted = balance.granted_days if balance else 0
    used = balance.used_days if balance else 0
    return LeaveBalanceResponse(
        user_id=current_user.id,
        user_name=current_user.name,
        year=target_year,
        granted_days=granted,
        used_days=used,
        remaining_days=granted - used,
    )


@router.get("/me", response_model=list[LeaveRequestResponse])
async def get_my_leaves(
    year: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[LeaveRequestResponse]:
    stmt = (
        select(LeaveRequest)
        .options(selectinload(LeaveRequest.user))
        .where(LeaveRequest.user_id == current_user.id)
        .order_by(LeaveRequest.created_at.desc())
    )
    if year:
        from sqlalchemy import extract
        stmt = stmt.where(extract("year", LeaveRequest.start_date) == year)

    result = await db.execute(stmt)
    records = result.scalars().all()
    return [_to_response(r) for r in records]


@router.delete("/{leave_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_leave(
    leave_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="申請が見つかりません")
    if record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="この申請をキャンセルする権限がありません")
    if record.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="承認待ち以外の申請はキャンセルできません")

    record.status = "CANCELLED"
    await db.commit()


@router.get("/pending", response_model=list[LeaveRequestResponse])
async def get_pending_leaves(
    _: User = Depends(require_manager_or_admin),
    db: AsyncSession = Depends(get_db),
) -> list[LeaveRequestResponse]:
    result = await db.execute(
        select(LeaveRequest)
        .options(selectinload(LeaveRequest.user))
        .where(LeaveRequest.status == "PENDING")
        .order_by(LeaveRequest.created_at.asc())
    )
    records = result.scalars().all()
    return [_to_response(r) for r in records]


@router.post("/{leave_id}/approve", response_model=LeaveRequestResponse)
async def approve_leave(
    leave_id: int,
    payload: ReviewRequest,
    current_user: User = Depends(require_manager_or_admin),
    db: AsyncSession = Depends(get_db),
) -> LeaveRequestResponse:
    result = await db.execute(
        select(LeaveRequest)
        .options(selectinload(LeaveRequest.user))
        .where(LeaveRequest.id == leave_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="申請が見つかりません")
    if record.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="承認待ち以外の申請は操作できません")

    # 有給承認時は残日数を減算
    if record.leave_type == "ANNUAL":
        year = record.start_date.year
        balance = await _get_balance(db, record.user_id, year)
        if balance is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="有給残日数が設定されていません",
            )
        remaining = balance.granted_days - balance.used_days
        if remaining < record.days:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"有給残日数が不足しています（残{remaining}日、申請{record.days}日）",
            )
        balance.used_days += record.days

    record.status = "APPROVED"
    record.reviewer_id = current_user.id
    record.reviewer_comment = payload.comment
    record.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(record)

    result2 = await db.execute(
        select(LeaveRequest)
        .options(selectinload(LeaveRequest.user))
        .where(LeaveRequest.id == record.id)
    )
    record = result2.scalar_one()
    return _to_response(record)


@router.post("/{leave_id}/reject", response_model=LeaveRequestResponse)
async def reject_leave(
    leave_id: int,
    payload: ReviewRequest,
    current_user: User = Depends(require_manager_or_admin),
    db: AsyncSession = Depends(get_db),
) -> LeaveRequestResponse:
    result = await db.execute(
        select(LeaveRequest)
        .options(selectinload(LeaveRequest.user))
        .where(LeaveRequest.id == leave_id)
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
        select(LeaveRequest)
        .options(selectinload(LeaveRequest.user))
        .where(LeaveRequest.id == record.id)
    )
    record = result2.scalar_one()
    return _to_response(record)
