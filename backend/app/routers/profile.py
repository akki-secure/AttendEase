import re

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

_ASCII_ONLY = re.compile(r'^[\x20-\x7E]+$')

from app.core.deps import get_current_user, get_db
from app.core.security import get_password_hash, verify_password
from app.models.user import User

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])


class ProfileResponse(BaseModel):
    id: int
    employee_id: str
    name: str
    email: str | None
    role: str

    model_config = {"from_attributes": True}


class ProfileUpdateRequest(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    current_password: str | None = None
    new_password: str | None = None


@router.get("/me", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
) -> ProfileResponse:
    return ProfileResponse(
        id=current_user.id,
        employee_id=current_user.employee_id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
    )


@router.patch("/me", response_model=ProfileResponse)
async def update_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    if payload.name is not None:
        current_user.name = payload.name

    if payload.email is not None:
        current_user.email = str(payload.email)

    if payload.new_password is not None:
        if not payload.current_password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="パスワード変更には現在のパスワードが必要です",
            )
        if not verify_password(payload.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="現在のパスワードが正しくありません",
            )
        if len(payload.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="新しいパスワードは8文字以上にしてください",
            )
        if not _ASCII_ONLY.match(payload.new_password):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="パスワードは英数字・記号（ASCII）のみ使用できます",
            )
        current_user.hashed_password = get_password_hash(payload.new_password)

    await db.commit()
    await db.refresh(current_user)

    return ProfileResponse(
        id=current_user.id,
        employee_id=current_user.employee_id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
    )
