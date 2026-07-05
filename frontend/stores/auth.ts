import { defineStore } from "pinia"
import type { AuthUser, LoginRequest, PreCheckResponse, TokenResponse } from "~/types/auth"
import { extractApiError } from "~/utils/validation"

export const useAuthStore = defineStore("auth", () => {
  const apiBase = useApiBase()
  const token = useCookie<string | null>("auth_token", { maxAge: 60 * 60 * 8, default: () => null })
  const user = ref<AuthUser | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  function decodeJwtUser(jwt: string): AuthUser {
    const decoded = JSON.parse(atob(jwt.split(".")[1]))
    return { id: decoded.user_id, employee_id: decoded.sub, name: decoded.name, role: decoded.role }
  }

  function isTokenExpired(jwt: string): boolean {
    try {
      const decoded = JSON.parse(atob(jwt.split(".")[1]))
      return typeof decoded.exp === "number" && decoded.exp * 1000 < Date.now()
    } catch {
      return true
    }
  }

  // トークンが残っていればリロード後も user を復元。
  // 期限切れの場合は「見た目はログイン状態だがAPIが全て401で通知等が一切来ない」状態を防ぐため即座に破棄する
  if (token.value) {
    if (isTokenExpired(token.value)) {
      token.value = null
    } else if (!user.value) {
      try {
        user.value = decodeJwtUser(token.value)
      } catch {
        token.value = null
      }
    }
  }

  // API呼び出しが401を返した場合の共通処理（トークン期限切れ等）
  function handleUnauthorized(err: unknown): boolean {
    const status = (err as { response?: { status?: number }; status?: number })?.response?.status
      ?? (err as { status?: number })?.status
    if (status === 401) {
      logout()
      return true
    }
    return false
  }

  function clearError() {
    error.value = null
  }

  async function preCheck(payload: { employee_id: string; password: string }): Promise<PreCheckResponse> {
    isLoading.value = true
    error.value = null
    try {
      const data = await $fetch<PreCheckResponse>(`${apiBase}/api/v1/auth/pre-check`, {
        method: "POST",
        body: payload,
      })
      return data
    } catch (err: unknown) {
      error.value = extractApiError(err, "認証に失敗しました。もう一度お試しください。")
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function login(payload: LoginRequest) {
    isLoading.value = true
    error.value = null

    try {
      const data = await $fetch<TokenResponse>(`${apiBase}/api/v1/auth/login`, {
        method: "POST",
        body: payload,
      })
      token.value = data.access_token
      user.value = decodeJwtUser(data.access_token)
      await navigateTo("/")
    } catch (err: unknown) {
      error.value = extractApiError(err, "ログインに失敗しました。もう一度お試しください。")
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    token.value = null
    user.value = null
    navigateTo("/login")
  }

  return { token, user, isLoading, error, isLoggedIn, clearError, preCheck, login, logout, handleUnauthorized }
})
