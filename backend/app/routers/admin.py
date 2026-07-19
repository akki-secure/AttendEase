from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_admin
from app.core.security import get_password_hash
from app.models.geofence_setting import GeofenceSetting
from app.models.leave_balance import LeaveBalance
from app.models.office_location import OfficeLocation
from app.models.user import User
from app.schemas.auth import AdminUserListItem, UserCreateRequest, UserResponse
from app.schemas.leave import LeaveBalanceResponse, LeaveBalanceUpdateRequest
from app.schemas.location import (
    GeofenceSettingResponse,
    GeofenceSettingUpdateRequest,
    LocationCreateRequest,
    LocationResponse,
    LocationUpdateRequest,
)

router = APIRouter()

VALID_ROLES = {"EMPLOYEE", "MANAGER", "ADMIN"}
_INITIAL_ANNUAL_LEAVE_DAYS = 3


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
    db.add(
        LeaveBalance(
            user_id=user.id,
            year=date.today().year,
            granted_days=_INITIAL_ANNUAL_LEAVE_DAYS,
            used_days=0,
        )
    )
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


def _to_admin_user_list_item(user: User) -> AdminUserListItem:
    return AdminUserListItem(
        id=user.id,
        employee_id=user.employee_id,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        email=user.email,
        is_locked=user.is_locked,
    )


@router.get("/users", response_model=list[AdminUserListItem])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[AdminUserListItem]:
    result = await db.execute(select(User).order_by(User.name))
    users = result.scalars().all()
    return [_to_admin_user_list_item(u) for u in users]


@router.patch("/users/{user_id}/unlock", response_model=AdminUserListItem)
async def unlock_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> AdminUserListItem:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")

    user.failed_login_count = 0
    await db.commit()
    await db.refresh(user)

    return _to_admin_user_list_item(user)


@router.get("/leave-balances", response_model=list[LeaveBalanceResponse])
async def get_leave_balances(
    year: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[LeaveBalanceResponse]:
    target_year = year or date.today().year

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


@router.get("/locations", response_model=list[LocationResponse])
async def get_locations(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[LocationResponse]:
    result = await db.execute(select(OfficeLocation).order_by(OfficeLocation.id))
    return list(result.scalars().all())


@router.post("/locations", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    payload: LocationCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> LocationResponse:
    location = OfficeLocation(
        name=payload.name,
        latitude=payload.latitude,
        longitude=payload.longitude,
        radius_meters=payload.radius_meters,
        is_active=payload.is_active,
    )
    db.add(location)
    await db.commit()
    await db.refresh(location)
    return location


@router.put("/locations/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: int,
    payload: LocationUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> LocationResponse:
    result = await db.execute(select(OfficeLocation).where(OfficeLocation.id == location_id))
    location = result.scalar_one_or_none()
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="拠点が見つかりません")

    location.name = payload.name
    location.latitude = payload.latitude
    location.longitude = payload.longitude
    location.radius_meters = payload.radius_meters
    location.is_active = payload.is_active
    await db.commit()
    await db.refresh(location)
    return location


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> None:
    result = await db.execute(select(OfficeLocation).where(OfficeLocation.id == location_id))
    location = result.scalar_one_or_none()
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="拠点が見つかりません")

    await db.delete(location)
    await db.commit()


@router.get("/geofence-settings", response_model=GeofenceSettingResponse)
async def get_geofence_settings(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> GeofenceSettingResponse:
    result = await db.execute(select(GeofenceSetting))
    setting = result.scalars().first()
    return GeofenceSettingResponse(enabled=setting.enabled if setting else False)


@router.put("/geofence-settings", response_model=GeofenceSettingResponse)
async def update_geofence_settings(
    payload: GeofenceSettingUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> GeofenceSettingResponse:
    result = await db.execute(select(GeofenceSetting))
    setting = result.scalars().first()
    if setting is None:
        setting = GeofenceSetting(enabled=payload.enabled)
        db.add(setting)
    else:
        setting.enabled = payload.enabled
    await db.commit()
    await db.refresh(setting)
    return GeofenceSettingResponse(enabled=setting.enabled)
