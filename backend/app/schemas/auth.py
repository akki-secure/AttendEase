from pydantic import BaseModel, EmailStr, field_validator

from app.core.security import ASCII_ONLY


class PreCheckRequest(BaseModel):
    employee_id: str
    password: str


class PreCheckResponse(BaseModel):
    ok: bool
    email_hint: str


class LoginRequest(BaseModel):
    employee_id: str
    otp: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _validate_password(v: str) -> str:
    if len(v) < 8:
        raise ValueError("パスワードは8文字以上で入力してください")
    if v.strip() == "":
        raise ValueError("パスワードにスペースのみは使用できません")
    if not ASCII_ONLY.match(v):
        raise ValueError("パスワードに使用できない文字が含まれています（日本語・全角文字は使用不可）")
    return v


class RegisterRequest(BaseModel):
    employee_id: str
    name: str
    password: str
    email: EmailStr | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password(v)


class UserCreateRequest(BaseModel):
    name: str
    employee_id: str
    password: str
    role: str = "EMPLOYEE"
    email: EmailStr | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password(v)


class UserResponse(BaseModel):
    id: int
    employee_id: str
    name: str
    role: str
    is_active: bool
    email: str | None = None


class PasswordResetRequestSchema(BaseModel):
    employee_id: str


class PasswordResetRequestResponse(BaseModel):
    ok: bool
    email_hint: str


class PasswordResetConfirmSchema(BaseModel):
    employee_id: str
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return _validate_password(v)
