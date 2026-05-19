import { defineStore } from "pinia"
import type { AuthUser, LoginRequest, TokenResponse } from "~/types/auth"

export const useAuthStore = defineStore("auth", () => {
  const config = useRuntimeConfig()
  const token = useCookie<string | null>("auth_token", { maxAge: 60 * 60 * 8, default: () => null })
  const user = ref<AuthUser | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(payload: LoginRequest) {
    isLoading.value = true
    error.value = null

    try {
      const data = await $fetch<TokenResponse>(`${config.public.apiBase}/api/v1/auth/login`, {
        method: "POST",
        body: payload,
      })
      token.value = data.access_token

      // JWT ペイロードから名前・社員IDを取得
      const payloadPart = data.access_token.split(".")[1]
      const decoded = JSON.parse(atob(payloadPart))
      user.value = { employee_id: decoded.sub, name: decoded.name, role: decoded.role }

      await navigateTo("/")
    } catch (err: unknown) {
      const fetchError = err as { data?: { detail?: string } }
      error.value = fetchError?.data?.detail ?? "ログインに失敗しました。もう一度お試しください。"
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

  return { token, user, isLoading, error, isLoggedIn, login, logout }
})
