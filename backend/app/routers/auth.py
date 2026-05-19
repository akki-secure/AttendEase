from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.core.security import create_access_token, dummy_verify, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter()

_ERROR_MSG = "社員IDまたはパスワードが正しくありません"


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    result = await db.execute(
        select(User).where(User.employee_id == payload.employee_id, User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()

    if user is None:
        dummy_verify()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_ERROR_MSG)

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_ERROR_MSG)

    token = create_access_token({"sub": user.employee_id, "name": user.name, "role": user.role})
    return TokenResponse(access_token=token)
