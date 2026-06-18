from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_admin
from app.core.security import get_password_hash
from app.models.leave_balance import LeaveBalance
from app.models.user import User
from app.schemas.auth import UserCreateRequest, UserResponse
from app.schemas.leave import LeaveBalanceResponse, LeaveBalanceUpdateRequest

router = APIRouter()

VALID_ROLES = {"EMPLOYEE", "MANAGER", "ADMIN"}


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> UserResponse:
    if payload.role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"ロールは {', '.join(VALID_ROLES)} のいずれかを指定してください",
        )

    existing = await db.execute(select(User).where(User.employee_id == payload.employee_id))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="その社員IDは既に使用されています",
        )

    user = User(
        employee_id=payload.employee_id,
        name=payload.name,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
    )
    db.add(user)
    await db.flush()

    initial_balance = LeaveBalance(
        user_id=user.id,
        year=datetime.now().year,
        granted_days=2,
        used_days=0,
    )
    db.add(initial_balance)
    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        employee_id=user.employee_id,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        email=user.email,
    )


@router.get("/leave-balances", response_model=list[LeaveBalanceResponse])
async def get_leave_balances(
    year: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[LeaveBalanceResponse]:
    from datetime import date as date_type

    target_year = year or date_type.today().year

    users_result = await db.execute(select(User).where(User.is_active.is_(True)).order_by(User.name))
    users = users_result.scalars().all()

    balances_result = await db.execute(
        select(LeaveBalance).where(LeaveBalance.year == target_year)
    )
    balances = {b.user_id: b for b in balances_result.scalars().all()}

    responses = []
    for u in users:
        b = balances.get(u.id)
        granted = b.granted_days if b else 0
        used = b.used_days if b else 0
        responses.append(
            LeaveBalanceResponse(
                user_id=u.id,
                user_name=u.name,
                year=target_year,
                granted_days=granted,
                used_days=used,
                remaining_days=granted - used,
            )
        )
    return responses


@router.put("/leave-balances/{user_id}/{year}", response_model=LeaveBalanceResponse)
async def update_leave_balance(
    user_id: int,
    year: int,
    payload: LeaveBalanceUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> LeaveBalanceResponse:
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")

    balance_result = await db.execute(
        select(LeaveBalance).where(LeaveBalance.user_id == user_id, LeaveBalance.year == year)
    )
    balance = balance_result.scalar_one_or_none()

    if balance is None:
        balance = LeaveBalance(user_id=user_id, year=year, granted_days=payload.granted_days, used_days=0)
        db.add(balance)
    else:
        balance.granted_days = payload.granted_days

    await db.commit()
    await db.refresh(balance)

    return LeaveBalanceResponse(
        user_id=user.id,
        user_name=user.name,
        year=balance.year,
        granted_days=balance.granted_days,
        used_days=balance.used_days,
        remaining_days=balance.granted_days - balance.used_days,
    )
