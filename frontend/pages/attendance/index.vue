<script setup lang="ts">
import type { MonthlyAttendanceResponse } from "~/types/attendance"

const authStore = useAuthStore()
const attendanceStore = useAttendanceStore()

if (!authStore.isLoggedIn) {
  await navigateTo("/login")
}

// 表示月（デフォルト: 今月）
const today = new Date()
const currentMonth = ref(
  `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}`
)

const monthly = ref<MonthlyAttendanceResponse | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

async function loadMonthly() {
  isLoading.value = true
  error.value = null
  try {
    monthly.value = await attendanceStore.fetchMonthly(currentMonth.value)
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    error.value = e?.data?.detail ?? "データの取得に失敗しました"
  } finally {
    isLoading.value = false
  }
}

await loadMonthly()
watch(currentMonth, loadMonthly)

function prevMonth() {
  const [y, m] = currentMonth.value.split("-").map(Number)
  const d = new Date(y, m - 2, 1)
  currentMonth.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`
}
function nextMonth() {
  const [y, m] = currentMonth.value.split("-").map(Number)
  const d = new Date(y, m, 1)
  currentMonth.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`
}

const isCurrentMonth = computed(() =>
  currentMonth.value === `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}`
)

function fmt(iso: string | null) {
  if (!iso) return "--:--"
  // Append 'Z' if no timezone info so the string is treated as UTC, not local time
  const utc = /[Z+]/.test(iso) ? iso : iso + "Z"
  return new Date(utc).toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" })
}
function fmtMinutes(min: number | null) {
  if (min == null) return "--"
  const h = Math.floor(min / 60)
  const m = min % 60
  return h > 0 ? `${h}:${String(m).padStart(2, "0")}` : `0:${String(m).padStart(2, "0")}`
}
function fmtDate(dateStr: string) {
  const d = new Date(dateStr + "T00:00:00")
  return d.toLocaleDateString("ja-JP", { month: "numeric", day: "numeric", weekday: "short" })
}

const statusMap: Record<string, { label: string; color: "green" | "blue" | "amber" | "gray" | "red" }> = {
  PRESENT:             { label: "出勤中",     color: "green" },
  CLOSED:              { label: "退勤済",     color: "blue" },
  CORRECTION_PENDING:  { label: "修正申請中", color: "amber" },
  CORRECTION_APPROVED: { label: "修正承認済", color: "green" },
}

const columns = [
  { key: "date",         label: "日付" },
  { key: "clock_in",    label: "出勤" },
  { key: "clock_out",   label: "退勤" },
  { key: "break",       label: "休憩" },
  { key: "work",        label: "労働時間" },
  { key: "overtime",    label: "残業" },
  { key: "status",      label: "状態" },
]

const tableRows = computed(() =>
  (monthly.value?.records ?? []).map((r) => {
    const overtime = r.work_minutes != null ? Math.max(r.work_minutes - 480, 0) : null
    return {
      ...r,
      _date:      fmtDate(r.date),
      _clockIn:   fmt(r.clock_in),
      _clockOut:  fmt(r.clock_out),
      _break:     r.break_minutes > 0 ? `${r.break_minutes}分` : "--",
      _work:      fmtMinutes(r.work_minutes),
      _overtime:  overtime != null && overtime > 0 ? fmtMinutes(overtime) : "--",
      _status:    statusMap[r.status] ?? { label: r.status, color: "gray" as const },
    }
  })
)

function fmtTotalHours(min: number) {
  const h = Math.floor(min / 60)
  const m = min % 60
  return `${h}時間${m}分`
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
    <!-- ヘッダー -->
    <header class="bg-gradient-to-r from-blue-700 to-indigo-800 shadow-lg">
      <div class="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <NuxtLink to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div class="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center shadow">
              <UIcon name="i-heroicons-clock" class="w-5 h-5 text-white" />
            </div>
            <span class="text-lg font-bold text-white">AttendEase</span>
          </NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-4 h-4 text-blue-300" />
          <span class="text-sm text-blue-100 font-medium">勤怠一覧</span>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-blue-100 hidden sm:block">{{ authStore.user?.name }} さん</span>
          <UButton variant="ghost" size="sm" icon="i-heroicons-arrow-right-on-rectangle" class="!bg-red-500 !text-white hover:!bg-red-600 transition-all duration-200 font-medium rounded-lg" @click="authStore.logout()">
            ログアウト
          </UButton>
        </div>
      </div>
    </header>

    <main class="max-w-5xl mx-auto px-6 py-10 space-y-6">
      <!-- 月選択 -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <UButton color="gray" variant="soft" icon="i-heroicons-chevron-left" @click="prevMonth" />
          <span class="text-xl font-bold text-gray-800 w-28 text-center">{{ currentMonth }}</span>
          <UButton
            color="gray" variant="soft" icon="i-heroicons-chevron-right"
            :disabled="isCurrentMonth"
            @click="nextMonth"
          />
        </div>
        <UButton color="gray" variant="outline" size="sm" @click="currentMonth = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`">
          今月
        </UButton>
      </div>

      <!-- サマリーカード -->
      <div v-if="monthly" class="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 text-center">
          <p class="text-xs text-gray-500 mb-1">出勤日数</p>
          <p class="text-2xl font-bold text-gray-800">{{ monthly.records.filter(r => r.clock_in).length }}<span class="text-sm font-normal text-gray-500 ml-1">日</span></p>
        </div>
        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 text-center">
          <p class="text-xs text-gray-500 mb-1">総労働時間</p>
          <p class="text-2xl font-bold text-blue-700">{{ fmtTotalHours(monthly.total_work_minutes) }}</p>
        </div>
        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 text-center col-span-2 sm:col-span-1">
          <p class="text-xs text-gray-500 mb-1">残業時間</p>
          <p class="text-2xl font-bold" :class="monthly.total_overtime_minutes > 0 ? 'text-orange-600' : 'text-gray-400'">
            {{ fmtTotalHours(monthly.total_overtime_minutes) }}
          </p>
        </div>
      </div>

      <!-- テーブル -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div v-if="isLoading" class="flex items-center justify-center py-16">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 text-gray-400 animate-spin" />
        </div>
        <div v-else-if="error" class="flex flex-col items-center justify-center py-16 gap-2">
          <UIcon name="i-heroicons-exclamation-circle" class="w-8 h-8 text-red-400" />
          <p class="text-gray-500 text-sm">{{ error }}</p>
        </div>
        <div v-else-if="tableRows.length === 0" class="flex flex-col items-center justify-center py-16 gap-2">
          <UIcon name="i-heroicons-calendar-days" class="w-8 h-8 text-gray-300" />
          <p class="text-gray-400 text-sm">この月の打刻記録はありません</p>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th v-for="col in columns" :key="col.key" class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">
                  {{ col.label }}
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr
                v-for="row in tableRows"
                :key="row.id"
                class="hover:bg-gray-50 transition-colors"
              >
                <td class="px-4 py-3 font-medium text-gray-700 whitespace-nowrap">{{ row._date }}</td>
                <td class="px-4 py-3 font-mono text-gray-600">{{ row._clockIn }}</td>
                <td class="px-4 py-3 font-mono text-gray-600">{{ row._clockOut }}</td>
                <td class="px-4 py-3 text-gray-500">{{ row._break }}</td>
                <td class="px-4 py-3 font-mono font-semibold text-gray-700">{{ row._work }}</td>
                <td class="px-4 py-3 font-mono" :class="row._overtime !== '--' ? 'text-orange-600 font-semibold' : 'text-gray-400'">{{ row._overtime }}</td>
                <td class="px-4 py-3">
                  <UBadge :color="row._status.color" variant="subtle" size="xs">
                    {{ row._status.label }}
                  </UBadge>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>
