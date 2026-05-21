export interface LoginRequest {
  employee_id: string
  password: string
  passphrase: string
}

export interface TokenResponse {
  access_token: string
  token_type: "bearer"
}

export interface AuthUser {
  employee_id: string
  name: string
  role: "EMPLOYEE" | "MANAGER" | "ADMIN"
}

export interface UserCreateRequest {
  name: string
  employee_id: string
  password: string
  role: "EMPLOYEE" | "MANAGER" | "ADMIN"
}

export interface UserResponse {
  id: number
  employee_id: string
  name: string
  role: string
  is_active: boolean
}
