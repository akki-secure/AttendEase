from pydantic import BaseModel


class PreCheckRequest(BaseModel):
    employee_id: str
    password: str


class LoginRequest(BaseModel):
    employee_id: str
    password: str
    passphrase: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    employee_id: str
    name: str
    password: str


class UserCreateRequest(BaseModel):
    name: str
    employee_id: str
    password: str
    role: str = "EMPLOYEE"


class UserResponse(BaseModel):
    id: int
    employee_id: str
    name: str
    role: str
    is_active: bool
