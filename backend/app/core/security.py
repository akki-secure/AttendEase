import re
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

ASCII_ONLY = re.compile(r"^[\x20-\x7E]+$")

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_DUMMY_HASH = pwd_context.hash("__dummy__")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def dummy_verify() -> None:
    """タイミング攻撃対策: ユーザーが存在しない場合でも同程度の処理時間を確保する"""
    pwd_context.verify("__dummy__", _DUMMY_HASH)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
