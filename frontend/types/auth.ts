export interface LoginRequest {
  employee_id: string
  otp: string
}

export interface PreCheckResponse {
  ok: boolean
  email_hint: string
}

export interface TokenResponse {
  access_token: string
  token_type: "bearer"
}

export interface AuthUser {
  id: number
  employee_id: string
  name: string
  role: "EMPLOYEE" | "MANAGER" | "ADMIN"
}

export interface UserCreateRequest {
  name: string
  employee_id: string
  password: string
  role: "EMPLOYEE" | "MANAGER" | "ADMIN"
  email?: string
}

export interface UserResponse {
  id: number
  employee_id: string
  name: string
  role: string
  is_active: boolean
  email?: string
}

export interface AdminUserListItem {
  id: number
  employee_id: string
  name: string
  role: string
  is_active: boolean
  email?: string
  is_locked: boolean
}
