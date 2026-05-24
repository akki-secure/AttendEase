import { defineStore } from "pinia"
import type { OvertimeCreatePayload, OvertimeMonthlySummary, OvertimeRequest, ReviewPayload } from "~/types/overtime"
import { extractApiError } from "~/utils/validation"

export const useOvertimeStore = defineStore("overtime", () => {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()

  const myOvertimes = ref<OvertimeRequest[]>([])
  const pendingOvertimes = ref<OvertimeRequest[]>([])
  const monthlySummary = ref<OvertimeMonthlySummary[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  function authHeaders() {
    return { Authorization: `Bearer ${authStore.token}` }
  }

  async function fetchMyOvertimes(year?: number): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const params = year ? { year } : {}
      myOvertimes.value = await $fetch<OvertimeRequest[]>(
        `${config.public.apiBase}/api/v1/overtime/me`,
        { headers: authHeaders(), params },
      )
    } catch (err: unknown) {
      error.value = extractApiError(err, "申請一覧の取得に失敗しました")
    } finally {
      isLoading.value = false
    }
  }

  async function createOvertime(payload: OvertimeCreatePayload): Promise<OvertimeRequest> {
    isLoading.value = true
    error.value = null
    try {
      const record = await $fetch<OvertimeRequest>(
        `${config.public.apiBase}/api/v1/overtime`,
        { method: "POST", headers: authHeaders(), body: payload },
      )
      await fetchMyOvertimes()
      return record
    } catch (err: unknown) {
      error.value = extractApiError(err, "申請の送信に失敗しました")
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function cancelOvertime(id: number): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      await $fetch(`${config.public.apiBase}/api/v1/overtime/${id}/cancel`, {
        method: "DELETE",
        headers: authHeaders(),
      })
      await fetchMyOvertimes()
    } catch (err: unknown) {
      error.value = extractApiError(err, "キャンセルに失敗しました")
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPendingOvertimes(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      pendingOvertimes.value = await $fetch<OvertimeRequest[]>(
        `${config.public.apiBase}/api/v1/overtime/pending`,
        { headers: authHeaders() },
      )
    } catch (err: unknown) {
      error.value = extractApiError(err, "承認待ち一覧の取得に失敗しました")
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMonthlySummary(year?: number, month?: number): Promise<void> {
    try {
      const params: Record<string, number> = {}
      if (year) params.year = year
      if (month) params.month = month
      monthlySummary.value = await $fetch<OvertimeMonthlySummary[]>(
        `${config.public.apiBase}/api/v1/overtime/monthly-summary`,
        { headers: authHeaders(), params },
      )
    } catch {
      monthlySummary.value = []
    }
  }

  async function approveOvertime(id: number, payload: ReviewPayload): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      await $fetch(`${config.public.apiBase}/api/v1/overtime/${id}/approve`, {
        method: "POST",
        headers: authHeaders(),
        body: payload,
      })
      await fetchPendingOvertimes()
    } catch (err: unknown) {
      error.value = extractApiError(err, "承認に失敗しました")
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function rejectOvertime(id: number, payload: ReviewPayload): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      await $fetch(`${config.public.apiBase}/api/v1/overtime/${id}/reject`, {
        method: "POST",
        headers: authHeaders(),
        body: payload,
      })
      await fetchPendingOvertimes()
    } catch (err: unknown) {
      error.value = extractApiError(err, "却下に失敗しました")
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    myOvertimes,
    pendingOvertimes,
    monthlySummary,
    isLoading,
    error,
    fetchMyOvertimes,
    createOvertime,
    cancelOvertime,
    fetchPendingOvertimes,
    fetchMonthlySummary,
    approveOvertime,
    rejectOvertime,
  }
})
