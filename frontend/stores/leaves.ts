import { defineStore } from "pinia"
import type { LeaveBalance, LeaveCreatePayload, LeaveRequest, ReviewPayload } from "~/types/leave"
import { extractApiError } from "~/utils/validation"

export const useLeaveStore = defineStore("leaves", () => {
  const apiBase = useApiBase()
  const authStore = useAuthStore()

  const myLeaves = ref<LeaveRequest[]>([])
  const pendingLeaves = ref<LeaveRequest[]>([])
  const myBalance = ref<LeaveBalance | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  function authHeaders() {
    return { Authorization: `Bearer ${authStore.token}` }
  }

  async function fetchMyLeaves(year?: number): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const params = year ? { year } : {}
      myLeaves.value = await $fetch<LeaveRequest[]>(
        `${apiBase}/api/v1/leaves/me`,
        { headers: authHeaders(), params },
      )
    } catch (err: unknown) {
      error.value = extractApiError(err, "申請一覧の取得に失敗しました")
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMyBalance(year?: number): Promise<void> {
    const targetYear = year ?? new Date().getFullYear()
    try {
      myBalance.value = await $fetch<LeaveBalance>(
        `${apiBase}/api/v1/leaves/my-balance`,
        { headers: authHeaders(), params: { year: targetYear } },
      )
    } catch {
      myBalance.value = null
    }
  }

  async function createLeave(payload: LeaveCreatePayload): Promise<LeaveRequest> {
    isLoading.value = true
    error.value = null
    try {
      const record = await $fetch<LeaveRequest>(
        `${apiBase}/api/v1/leaves`,
        { method: "POST", headers: authHeaders(), body: payload },
      )
      await fetchMyLeaves()
      return record
    } catch (err: unknown) {
      error.value = extractApiError(err, "申請の送信に失敗しました")
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function cancelLeave(id: number): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      await $fetch(`${apiBase}/api/v1/leaves/${id}/cancel`, {
        method: "DELETE",
        headers: authHeaders(),
      })
      await fetchMyLeaves()
    } catch (err: unknown) {
      error.value = extractApiError(err, "キャンセルに失敗しました")
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPendingLeaves(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      pendingLeaves.value = await $fetch<LeaveRequest[]>(
        `${apiBase}/api/v1/leaves/pending`,
        { headers: authHeaders() },
      )
    } catch (err: unknown) {
      error.value = extractApiError(err, "承認待ち一覧の取得に失敗しました")
    } finally {
      isLoading.value = false
    }
  }

  async function approveLeave(id: number, payload: ReviewPayload): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      await $fetch(`${apiBase}/api/v1/leaves/${id}/approve`, {
        method: "POST",
        headers: authHeaders(),
        body: payload,
      })
      await fetchPendingLeaves()
    } catch (err: unknown) {
      error.value = extractApiError(err, "承認に失敗しました")
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function rejectLeave(id: number, payload: ReviewPayload): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      await $fetch(`${apiBase}/api/v1/leaves/${id}/reject`, {
        method: "POST",
        headers: authHeaders(),
        body: payload,
      })
      await fetchPendingLeaves()
    } catch (err: unknown) {
      error.value = extractApiError(err, "却下に失敗しました")
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    myLeaves,
    pendingLeaves,
    myBalance,
    isLoading,
    error,
    fetchMyLeaves,
    fetchMyBalance,
    createLeave,
    cancelLeave,
    fetchPendingLeaves,
    approveLeave,
    rejectLeave,
  }
})
