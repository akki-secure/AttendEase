from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.core.security import create_access_token, dummy_verify, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, PreCheckRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter()

_ERROR_MSG = "社員IDまたはパスワードが正しくありません"
_LOCK_MSG = "アカウントがロックされています。管理者にお問い合わせください。"
_MAX_FAILED_ATTEMPTS = 3
_SECRET_PHRASE = "働いて働いて働いて働いて働いてまいります"


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> UserResponse:
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
        role="EMPLOYEE",
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


@router.post("/pre-check", status_code=status.HTTP_200_OK)
async def pre_check(payload: PreCheckRequest, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(
        select(User).where(User.employee_id == payload.employee_id, User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()

    if user is None:
        dummy_verify()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_ERROR_MSG)

    if user.failed_login_count >= _MAX_FAILED_ATTEMPTS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=_LOCK_MSG)

    if not verify_password(payload.password, user.hashed_password):
        user.failed_login_count += 1
        await db.commit()
        remaining = _MAX_FAILED_ATTEMPTS - user.failed_login_count
        if remaining <= 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=_LOCK_MSG)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{_ERROR_MSG}（残り{remaining}回失敗するとアカウントがロックされます）",
        )

    return {"ok": True}


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    result = await db.execute(
        select(User).where(User.employee_id == payload.employee_id, User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()

    if user is None:
        dummy_verify()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_ERROR_MSG)

    if user.failed_login_count >= _MAX_FAILED_ATTEMPTS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=_LOCK_MSG)

    if payload.passphrase != _SECRET_PHRASE:
        user.failed_login_count += 1
        await db.commit()
        remaining = _MAX_FAILED_ATTEMPTS - user.failed_login_count
        if remaining <= 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=_LOCK_MSG)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"合言葉が正しくありません（残り{remaining}回失敗するとアカウントがロックされます）",
        )

    if user.failed_login_count != 0:
        user.failed_login_count = 0
        await db.commit()

    token = create_access_token({"sub": user.employee_id, "name": user.name, "role": user.role})
    return TokenResponse(access_token=token)
