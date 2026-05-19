from pydantic import BaseModel


class LoginRequest(BaseModel):
    employee_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


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
