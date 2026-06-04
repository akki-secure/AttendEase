import { defineStore } from "pinia"
import type { AttendanceRecord, MonthlyAttendanceResponse, TodayStatusResponse, WorkType, YearlySummaryResponse } from "~/types/attendance"
import { extractApiError } from "~/utils/validation"

export const useAttendanceStore = defineStore("attendance", () => {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()

  const today = ref<TodayStatusResponse | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  function authHeaders() {
    return { Authorization: `Bearer ${authStore.token}` }
  }

  async function fetchToday() {
    isLoading.value = true
    error.value = null
    try {
      today.value = await $fetch<TodayStatusResponse>(
        `${config.public.apiBase}/api/v1/attendance/today`,
        { headers: authHeaders() },
      )
    } catch (err: unknown) {
      error.value = extractApiError(err, "状態の取得に失敗しました")
    } finally {
      isLoading.value = false
    }
  }

  async function clockIn(clockInIso?: string, workType?: WorkType): Promise<AttendanceRecord> {
    isLoading.value = true
    error.value = null
    try {
      const body: Record<string, unknown> = {}
      if (clockInIso) body.clock_in = clockInIso
      if (workType) body.work_type = workType
      const record = await $fetch<AttendanceRecord>(
        `${config.public.apiBase}/api/v1/attendance/clock-in`,
        { method: "POST", headers: authHeaders(), body },
      )
      await fetchToday()
      return record
    } catch (err: unknown) {
      error.value = extractApiError(err, "出勤打刻に失敗しました")
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function clockOut(clockOutIso?: string): Promise<AttendanceRecord> {
    isLoading.value = true
    error.value = null
    try {
      const body = clockOutIso ? { clock_out: clockOutIso } : {}
      const record = await $fetch<AttendanceRecord>(
        `${config.public.apiBase}/api/v1/attendance/clock-out`,
        { method: "POST", headers: authHeaders(), body },
      )
      await fetchToday()
      return record
    } catch (err: unknown) {
      error.value = extractApiError(err, "退勤打刻に失敗しました")
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fixClockIn(clockInIso: string, workType?: WorkType): Promise<AttendanceRecord> {
    isLoading.value = true
    error.value = null
    try {
      const body: Record<string, unknown> = { clock_in: clockInIso }
      if (workType) body.work_type = workType
      const record = await $fetch<AttendanceRecord>(
        `${config.public.apiBase}/api/v1/attendance/today/clock-in`,
        { method: "PATCH", headers: authHeaders(), body },
      )
      await fetchToday()
      return record
    } catch (err: unknown) {
      error.value = extractApiError(err, "出勤時刻の修正に失敗しました")
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fixClockOut(clockOutIso: string): Promise<AttendanceRecord> {
    isLoading.value = true
    error.value = null
    try {
      const record = await $fetch<AttendanceRecord>(
        `${config.public.apiBase}/api/v1/attendance/today/clock-out`,
        { method: "PATCH", headers: authHeaders(), body: { clock_out: clockOutIso } },
      )
      await fetchToday()
      return record
    } catch (err: unknown) {
      error.value = extractApiError(err, "退勤時刻の修正に失敗しました")
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function requestCorrection(
    recordId: number,
    clockIn: string,
    clockOut: string,
    note: string,
    breakMinutes = 0,
  ): Promise<AttendanceRecord> {
    isLoading.value = true
    error.value = null
    try {
      const record = await $fetch<AttendanceRecord>(
        `${config.public.apiBase}/api/v1/attendance/${recordId}/correction-request`,
        {
          method: "PATCH",
          headers: authHeaders(),
          body: { clock_in: clockIn, clock_out: clockOut, break_minutes: breakMinutes, note },
        },
      )
      await fetchToday()
      return record
    } catch (err: unknown) {
      error.value = extractApiError(err, "修正申請に失敗しました")
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createPastRecord(
    date: string,
    clockIn: string,
    clockOut: string,
    workType: WorkType | null,
    breakMinutes: number,
  ): Promise<AttendanceRecord> {
    try {
      return await $fetch<AttendanceRecord>(
        `${config.public.apiBase}/api/v1/attendance/record`,
        {
          method: "POST",
          headers: authHeaders(),
          body: { date, clock_in: clockIn, clock_out: clockOut, work_type: workType, break_minutes: breakMinutes },
        },
      )
    } catch (err: unknown) {
      throw err
    }
  }

  async function fetchMonthly(month: string): Promise<MonthlyAttendanceResponse> {
    return $fetch<MonthlyAttendanceResponse>(
      `${config.public.apiBase}/api/v1/attendance/me`,
      { params: { month }, headers: authHeaders() },
    )
  }

  async function fetchYearly(year: number): Promise<YearlySummaryResponse> {
    return $fetch<YearlySummaryResponse>(
      `${config.public.apiBase}/api/v1/attendance/me/yearly`,
      { params: { year }, headers: authHeaders() },
    )
  }

  return { today, isLoading, error, fetchToday, clockIn, clockOut, fixClockIn, fixClockOut, requestCorrection, createPastRecord, fetchMonthly, fetchYearly }
})
