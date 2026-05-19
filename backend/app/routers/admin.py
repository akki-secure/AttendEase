from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_admin
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.auth import UserCreateRequest, UserResponse

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
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        employee_id=user.employee_id,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
    )
