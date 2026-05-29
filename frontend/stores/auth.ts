import { defineStore } from "pinia"
import type { AuthUser, LoginRequest, PreCheckResponse, TokenResponse } from "~/types/auth"
import { extractApiError } from "~/utils/validation"

export const useAuthStore = defineStore("auth", () => {
  const config = useRuntimeConfig()
  const token = useCookie<string | null>("auth_token", { maxAge: 60 * 60 * 8, default: () => null })
  const user = ref<AuthUser | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  function decodeJwtUser(jwt: string): AuthUser {
    const decoded = JSON.parse(atob(jwt.split(".")[1]))
    return { id: decoded.user_id, employee_id: decoded.sub, name: decoded.name, role: decoded.role }
  }

  // トークンが残っていればリロード後も user を復元
  if (token.value && !user.value) {
    try {
      user.value = decodeJwtUser(token.value)
    } catch {
      token.value = null
    }
  }

  function clearError() {
    error.value = null
  }

  async function preCheck(payload: { employee_id: string; password: string }): Promise<PreCheckResponse> {
    isLoading.value = true
    error.value = null
    try {
      const data = await $fetch<PreCheckResponse>(`${config.public.apiBase}/api/v1/auth/pre-check`, {
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
      const data = await $fetch<TokenResponse>(`${config.public.apiBase}/api/v1/auth/login`, {
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

  return { token, user, isLoading, error, isLoggedIn, clearError, preCheck, login, logout }
})
