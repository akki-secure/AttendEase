from pydantic import BaseModel, EmailStr


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


class RegisterRequest(BaseModel):
    employee_id: str
    name: str
    password: str
    email: EmailStr | None = None


class UserCreateRequest(BaseModel):
    name: str
    employee_id: str
    password: str
    role: str = "EMPLOYEE"
    email: EmailStr | None = None


class UserResponse(BaseModel):
    id: int
    employee_id: str
    name: str
    role: str
    is_active: bool
    email: str | None = None
