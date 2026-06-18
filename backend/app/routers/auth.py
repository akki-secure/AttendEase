import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.deps import get_db
from app.core.email import send_otp_email, send_password_reset_email
from app.core.security import create_access_token, dummy_verify, get_password_hash, verify_password
from app.models.otp import OtpCode
from app.models.password_reset_token import PasswordResetToken
from app.models.leave_balance import LeaveBalance
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    PasswordResetConfirmSchema,
    PasswordResetRequestResponse,
    PasswordResetRequestSchema,
    PreCheckRequest,
    PreCheckResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter()

_ERROR_MSG = "社員IDまたはパスワードが正しくありません"
_LOCK_MSG = "アカウントがロックされています。管理者にお問い合わせください。"
_MAX_FAILED_ATTEMPTS = 3


def _mask_email(email: str) -> str:
    local, domain = email.split("@", 1)
    return local[:2] + "***@" + domain


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> UserResponse:
    existing = await db.execute(select(User).where(User.employee_id == payload.employee_id))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="その社員IDは既に使用されています",
        )

    if payload.email is not None:
        email_existing = await db.execute(select(User).where(User.email == payload.email))
        if email_existing.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="そのメールアドレスは既に使用されています",
            )

    user = User(
        employee_id=payload.employee_id,
        name=payload.name,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        role="EMPLOYEE",
    )
    db.add(user)
    await db.flush()

    current_year = datetime.now(timezone.utc).year
    leave_balance = LeaveBalance(user_id=user.id, year=current_year, granted_days=2, used_days=0)
    db.add(leave_balance)

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


@router.post("/pre-check", response_model=PreCheckResponse, status_code=status.HTTP_200_OK)
async def pre_check(payload: PreCheckRequest, db: AsyncSession = Depends(get_db)) -> PreCheckResponse:
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

    if not user.email:
        if not settings.DEV_OTP_BYPASS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="メールアドレスが未登録です。管理者にお問い合わせください。",
            )

    # 再送信レート制限チェック
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent_result = await db.execute(
        select(OtpCode)
        .where(OtpCode.employee_id == payload.employee_id, OtpCode.used.is_(False))
        .order_by(OtpCode.created_at.desc())
    )
    recent = recent_result.scalar_one_or_none()
    if recent is not None:
        elapsed = (now - recent.created_at).total_seconds()
        if elapsed < settings.OTP_RESEND_INTERVAL_SECONDS:
            wait = int(settings.OTP_RESEND_INTERVAL_SECONDS - elapsed)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"再送信は{wait}秒後に可能です",
            )

    # 古い未使用OTPを削除してから新規作成
    await db.execute(
        delete(OtpCode).where(OtpCode.employee_id == payload.employee_id, OtpCode.used.is_(False))
    )

    code = str(secrets.randbelow(1_000_000)).zfill(6)
    hashed_code = get_password_hash(code)
    expires_at = now + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

    db.add(OtpCode(employee_id=payload.employee_id, code=hashed_code, expires_at=expires_at))
    await db.commit()

    if settings.DEV_OTP_BYPASS:
        return PreCheckResponse(ok=True, email_hint=f"[DEV] {code}")

    send_otp_email(user.email, code)
    return PreCheckResponse(ok=True, email_hint=_mask_email(user.email))


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

    # 期限切れOTPをクリーンアップ
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.execute(delete(OtpCode).where(OtpCode.expires_at < now))

    otp_result = await db.execute(
        select(OtpCode)
        .where(
            OtpCode.employee_id == payload.employee_id,
            OtpCode.used.is_(False),
            OtpCode.expires_at > now,
        )
        .order_by(OtpCode.created_at.desc())
    )
    otp_record = otp_result.scalar_one_or_none()

    if otp_record is None or not verify_password(payload.otp, otp_record.code):
        user.failed_login_count += 1
        await db.commit()
        remaining = _MAX_FAILED_ATTEMPTS - user.failed_login_count
        if remaining <= 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=_LOCK_MSG)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"認証コードが正しくありません（残り{remaining}回失敗するとアカウントがロックされます）",
        )

    otp_record.used = True
    if user.failed_login_count != 0:
        user.failed_login_count = 0
    await db.commit()

    token = create_access_token({"sub": user.employee_id, "name": user.name, "role": user.role, "user_id": user.id})
    return TokenResponse(access_token=token)


@router.post("/password-reset/request", response_model=PasswordResetRequestResponse)
async def password_reset_request(
    payload: PasswordResetRequestSchema, db: AsyncSession = Depends(get_db)
) -> PasswordResetRequestResponse:
    result = await db.execute(select(User).where(User.employee_id == payload.employee_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()

    # ユーザーが存在しない場合でも同じレスポンスを返す（ユーザー列挙攻撃対策）
    if user is None or not user.email:
        if settings.DEV_OTP_BYPASS:
            return PasswordResetRequestResponse(ok=True, email_hint="[DEV] no-email")
        return PasswordResetRequestResponse(ok=True, email_hint="re***@example.com")

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    # 再送信レート制限
    recent_result = await db.execute(
        select(PasswordResetToken)
        .where(PasswordResetToken.employee_id == payload.employee_id, PasswordResetToken.used.is_(False))
        .order_by(PasswordResetToken.created_at.desc())
    )
    recent = recent_result.scalar_one_or_none()
    if recent is not None:
        elapsed = (now - recent.created_at).total_seconds()
        if elapsed < settings.RESET_RESEND_INTERVAL_SECONDS:
            wait = int(settings.RESET_RESEND_INTERVAL_SECONDS - elapsed)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"再送信は{wait}秒後に可能です",
            )

    # 古い未使用トークンを削除してから新規作成
    await db.execute(
        delete(PasswordResetToken).where(
            PasswordResetToken.employee_id == payload.employee_id, PasswordResetToken.used.is_(False)
        )
    )

    code = str(secrets.randbelow(1_000_000)).zfill(6)
    hashed_code = get_password_hash(code)
    expires_at = now + timedelta(minutes=settings.RESET_EXPIRE_MINUTES)
    db.add(PasswordResetToken(employee_id=payload.employee_id, code=hashed_code, expires_at=expires_at))
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"再送信は{settings.RESET_RESEND_INTERVAL_SECONDS}秒後に可能です",
        )

    if settings.DEV_OTP_BYPASS:
        return PasswordResetRequestResponse(ok=True, email_hint=f"[DEV] {code}")

    send_password_reset_email(user.email, code)
    return PasswordResetRequestResponse(ok=True, email_hint=_mask_email(user.email))


@router.post("/password-reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def password_reset_confirm(
    payload: PasswordResetConfirmSchema, db: AsyncSession = Depends(get_db)
) -> None:
    result = await db.execute(select(User).where(User.employee_id == payload.employee_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="認証コードが正しくありません")

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.execute(delete(PasswordResetToken).where(PasswordResetToken.expires_at < now))

    token_result = await db.execute(
        select(PasswordResetToken)
        .where(
            PasswordResetToken.employee_id == payload.employee_id,
            PasswordResetToken.used.is_(False),
            PasswordResetToken.expires_at > now,
        )
        .order_by(PasswordResetToken.created_at.desc())
    )
    token_record = token_result.scalar_one_or_none()

    if token_record is None or not verify_password(payload.token, token_record.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="認証コードが正しくありません")

    token_record.used = True
    user.hashed_password = get_password_hash(payload.new_password)
    user.failed_login_count = 0
    await db.commit()
