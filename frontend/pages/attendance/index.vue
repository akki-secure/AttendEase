<script setup lang="ts">
import type { MonthlyAttendanceResponse } from "~/types/attendance"
import type { WorkType } from "~/types/attendance"
import type { LeaveRequest } from "~/types/leave"

const authStore = useAuthStore()
const attendanceStore = useAttendanceStore()
const leaveStore = useLeaveStore()

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

// 休暇データ（当年分を一括取得）
const myLeaves = ref<LeaveRequest[]>([])
async function loadLeaves() {
  try {
    await leaveStore.fetchMyLeaves(today.getFullYear())
    myLeaves.value = leaveStore.myLeaves
  } catch { /* non-critical */ }
}

await Promise.all([loadMonthly(), loadLeaves()])
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
  { key: "work_type",   label: "形態" },
  { key: "clock_in",    label: "出勤" },
  { key: "clock_out",   label: "退勤" },
  { key: "break",       label: "休憩" },
  { key: "work",        label: "労働時間" },
  { key: "overtime",    label: "残業" },
  { key: "status",      label: "状態" },
]

const tableRows = computed(() =>
  (monthly.value?.records ?? []).map((r) => {
    const rawOvertime = r.work_minutes != null ? Math.max(r.work_minutes - 480, 0) : null
    const overtime = rawOvertime != null ? Math.floor(rawOvertime / 15) * 15 : null
    const workTypeLabel = r.work_type === "office" ? "出社" : r.work_type === "remote" ? "リモート" : null
    return {
      ...r,
      _date:      fmtDate(r.date),
      _workType:  workTypeLabel,
      _workTypeColor: r.work_type === "office" ? ("green" as const) : r.work_type === "remote" ? ("blue" as const) : undefined,
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

// ─── カレンダー ───────────────────────────────────────
const WEEKDAYS = ["日", "月", "火", "水", "木", "金", "土"]

const calendarDays = computed(() => {
  const [y, m] = currentMonth.value.split("-").map(Number)
  const firstDay = new Date(y, m - 1, 1).getDay() // 0=日
  const daysInMonth = new Date(y, m, 0).getDate()
  const cells: Array<{ date: string; day: number } | null> = []
  for (let i = 0; i < firstDay; i++) cells.push(null)
  for (let d = 1; d <= daysInMonth; d++) {
    cells.push({ date: `${y}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`, day: d })
  }
  return cells
})

const recordByDate = computed(() => {
  const map: Record<string, (typeof tableRows.value)[0]> = {}
  for (const r of tableRows.value) map[r.date] = r
  return map
})

const todayStr = computed(
  () => `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`
)

const LEAVE_TYPE_JA: Record<string, string> = {
  ANNUAL: "有給",
  SPECIAL: "特別休暇",
  LATE: "遅刻",
  EARLY_LEAVE: "早退",
}

// 日付ごとの休暇マップ（APPROVED または PENDING のみ）
const leaveByDate = computed(() => {
  const map: Record<string, LeaveRequest> = {}
  for (const leave of myLeaves.value) {
    if (leave.status === "REJECTED" || leave.status === "CANCELLED") continue
    const start = new Date(leave.start_date + "T00:00:00")
    const end = new Date(leave.end_date + "T00:00:00")
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`
      map[key] = leave
    }
  }
  return map
})

function cellState(dateStr: string): "today" | "past-leave" | "past-empty" | "past-recorded" | "future" {
  if (dateStr === todayStr.value) return "today"
  if (dateStr < todayStr.value) {
    if (leaveByDate.value[dateStr]) return "past-leave"
    return recordByDate.value[dateStr] ? "past-recorded" : "past-empty"
  }
  return "future"
}

// ─── 過去打刻入力モーダル ─────────────────────────────
const modalOpen = ref(false)
const modalDate = ref("")
const modalClockIn = ref("09:00")
const modalClockOut = ref("18:00")
const modalWorkType = ref<WorkType | "">("")
const modalBreak = ref(60)
const modalError = ref<string | null>(null)
const modalLoading = ref(false)

function openModal(dateStr: string) {
  modalDate.value = dateStr
  modalClockIn.value = "09:00"
  modalClockOut.value = "18:00"
  modalWorkType.value = ""
  modalBreak.value = 60
  modalError.value = null
  modalOpen.value = true
}

function toIsoJst(dateStr: string, timeStr: string): string {
  return new Date(`${dateStr}T${timeStr}:00+09:00`).toISOString()
}

// 退勤時刻が出勤時刻より前 = 日をまたぐ勤務（夜勤）とみなし翌日として扱う
function toIsoJstClockOut(dateStr: string, timeStr: string, clockInIso: string): string {
  const d = new Date(`${dateStr}T${timeStr}:00+09:00`)
  if (d.getTime() < new Date(clockInIso).getTime()) {
    d.setDate(d.getDate() + 1)
  }
  return d.toISOString()
}

async function submitPastRecord() {
  modalError.value = null
  if (!modalClockIn.value || !modalClockOut.value) {
    modalError.value = "出勤・退勤時刻を入力してください"
    return
  }
  if (!modalWorkType.value) {
    modalError.value = "出社形態を選択してください"
    return
  }
  modalLoading.value = true
  try {
    const clockInIso = toIsoJst(modalDate.value, modalClockIn.value)
    await attendanceStore.createPastRecord(
      modalDate.value,
      clockInIso,
      toIsoJstClockOut(modalDate.value, modalClockOut.value, clockInIso),
      modalWorkType.value as WorkType,
      modalBreak.value,
    )
    modalOpen.value = false
    await loadMonthly()
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    modalError.value = e?.data?.detail ?? "登録に失敗しました"
  } finally {
    modalLoading.value = false
  }
}

const { roleTheme } = useRoleTheme()
</script>

<template>
  <div :class="['min-h-screen', roleTheme.pageBg]">
    <!-- ヘッダー -->
    <header :class="[roleTheme.header, 'shadow-lg']">
      <div class="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <NuxtLink to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div class="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center shadow">
              <UIcon name="i-heroicons-clock" class="w-5 h-5 text-white" />
            </div>
            <span class="text-lg font-bold text-white">AttendEase</span>
          </NuxtLink>
          <UIcon name="i-heroicons-chevron-right" :class="['w-4 h-4', roleTheme.sub3]" />
          <span :class="['text-sm font-medium', roleTheme.sub1]">勤怠一覧</span>
        </div>
        <div class="flex items-center gap-3">
          <span :class="['text-sm hidden sm:block', roleTheme.sub1]">{{ authStore.user?.name }} さん</span>
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
          <p class="text-2xl font-bold text-brand-700">{{ fmtTotalHours(monthly.total_work_minutes) }}</p>
        </div>
        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 text-center col-span-2 sm:col-span-1">
          <p class="text-xs text-gray-500 mb-1">残業時間</p>
          <p class="text-2xl font-bold" :class="monthly.total_overtime_minutes > 0 ? 'text-orange-600' : 'text-gray-400'">
            {{ fmtTotalHours(monthly.total_overtime_minutes) }}
          </p>
        </div>
      </div>

      <!-- カレンダー -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
        <div class="flex items-center gap-2 mb-4">
          <UIcon name="i-heroicons-calendar-days" class="w-4 h-4 text-gray-400" />
          <span class="text-sm font-semibold text-gray-600">月間カレンダー</span>
          <span v-if="isCurrentMonth" class="ml-2 text-xs text-gray-400">過去の未入力日をクリックして打刻を追加できます</span>
        </div>
        <!-- 曜日ヘッダー -->
        <div class="grid grid-cols-7 mb-1">
          <div
            v-for="(wd, i) in WEEKDAYS" :key="wd"
            class="text-center text-xs font-semibold py-1"
            :class="i === 0 ? 'text-red-400' : i === 6 ? 'text-blue-400' : 'text-gray-400'"
          >{{ wd }}</div>
        </div>
        <!-- 日付グリッド -->
        <div class="grid grid-cols-7 gap-1">
          <div v-for="(cell, idx) in calendarDays" :key="idx">
            <!-- 空白セル（月初の埋め） -->
            <div v-if="!cell" class="h-14" />
            <!-- 今日 -->
            <div
              v-else-if="cellState(cell.date) === 'today'"
              class="h-14 rounded-xl border-2 border-brand-400 bg-brand-50 flex flex-col items-center justify-center px-1"
            >
              <span class="text-xs font-bold text-brand-600">{{ cell.day }}</span>
              <span class="text-[10px] text-brand-400 mt-0.5">今日</span>
            </div>
            <!-- 過去・休暇あり -->
            <div
              v-else-if="cellState(cell.date) === 'past-leave'"
              class="h-14 rounded-xl flex flex-col items-center justify-center px-1"
              :class="leaveByDate[cell.date].status === 'APPROVED' ? 'bg-green-50 border border-green-100' : 'bg-amber-50 border border-amber-100'"
            >
              <span class="text-xs font-semibold" :class="leaveByDate[cell.date].status === 'APPROVED' ? 'text-green-700' : 'text-amber-700'">{{ cell.day }}</span>
              <span
                class="text-[10px] mt-0.5 font-medium leading-tight text-center"
                :class="leaveByDate[cell.date].status === 'APPROVED' ? 'text-green-500' : 'text-amber-500'"
              >{{ LEAVE_TYPE_JA[leaveByDate[cell.date].leave_type] ?? leaveByDate[cell.date].leave_type }}</span>
              <span v-if="leaveByDate[cell.date].status === 'PENDING'" class="text-[9px] text-amber-400">申請中</span>
            </div>
            <!-- 過去・記録あり -->
            <div
              v-else-if="cellState(cell.date) === 'past-recorded'"
              class="h-14 rounded-xl bg-blue-50 border border-blue-100 flex flex-col items-center justify-center px-1"
            >
              <span class="text-xs font-semibold text-gray-600">{{ cell.day }}</span>
              <span class="text-[10px] text-blue-500 mt-0.5 font-mono leading-tight">{{ recordByDate[cell.date]._clockIn }}</span>
              <span class="text-[10px] text-blue-400 font-mono leading-tight">{{ recordByDate[cell.date]._clockOut }}</span>
            </div>
            <!-- 過去・未入力（当月のみクリック可） -->
            <button
              v-else-if="cellState(cell.date) === 'past-empty'"
              class="h-14 w-full rounded-xl border border-dashed border-gray-200 hover:border-brand-300 hover:bg-brand-50 flex flex-col items-center justify-center transition-colors group"
              @click="openModal(cell.date)"
            >
              <span class="text-xs text-gray-400 group-hover:text-brand-500">{{ cell.day }}</span>
              <UIcon name="i-heroicons-plus" class="w-3.5 h-3.5 text-gray-300 group-hover:text-brand-400 mt-0.5" />
            </button>
            <!-- 未来 -->
            <div
              v-else
              class="h-14 rounded-xl flex items-center justify-center"
            >
              <span class="text-xs text-gray-300">{{ cell.day }}</span>
            </div>
          </div>
        </div>
        <!-- 凡例 -->
        <div class="flex flex-wrap items-center gap-4 mt-4 pt-3 border-t border-gray-50">
          <div class="flex items-center gap-1.5"><div class="w-3 h-3 rounded bg-blue-100 border border-blue-200" /><span class="text-xs text-gray-400">打刻済</span></div>
          <div class="flex items-center gap-1.5"><div class="w-3 h-3 rounded border border-dashed border-gray-300" /><span class="text-xs text-gray-400">未入力（クリックで追加）</span></div>
          <div class="flex items-center gap-1.5"><div class="w-3 h-3 rounded bg-green-100 border border-green-200" /><span class="text-xs text-gray-400">休暇（承認済）</span></div>
          <div class="flex items-center gap-1.5"><div class="w-3 h-3 rounded bg-amber-100 border border-amber-200" /><span class="text-xs text-gray-400">休暇（申請中）</span></div>
          <div class="flex items-center gap-1.5"><div class="w-3 h-3 rounded border-2 border-brand-400 bg-brand-50" /><span class="text-xs text-gray-400">今日</span></div>
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
                <td class="px-4 py-3">
                  <UBadge v-if="row._workType" :color="row._workTypeColor" variant="subtle" size="xs">{{ row._workType }}</UBadge>
                  <span v-else class="text-gray-300">—</span>
                </td>
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

    <!-- 過去日付入力モーダル -->
    <UModal v-model="modalOpen">
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-pencil-square" class="w-5 h-5 text-brand-500" />
            <span class="font-semibold text-gray-800">打刻を入力</span>
            <UBadge color="gray" variant="soft" size="xs">{{ modalDate }}</UBadge>
          </div>
        </template>

        <div class="space-y-4">
          <!-- 出社形態 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">出社形態 <span class="text-red-500">*</span></label>
            <div class="flex gap-2">
              <UButton
                size="sm"
                :color="modalWorkType === 'office' ? 'green' : 'gray'"
                :variant="modalWorkType === 'office' ? 'solid' : 'outline'"
                @click="modalWorkType = modalWorkType === 'office' ? '' : 'office'"
              >出社</UButton>
              <UButton
                size="sm"
                :color="modalWorkType === 'remote' ? 'blue' : 'gray'"
                :variant="modalWorkType === 'remote' ? 'solid' : 'outline'"
                @click="modalWorkType = modalWorkType === 'remote' ? '' : 'remote'"
              >リモート</UButton>
            </div>
          </div>

          <!-- 出勤時刻 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">出勤時刻</label>
            <input
              v-model="modalClockIn"
              type="time"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400"
            />
          </div>

          <!-- 退勤時刻 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">退勤時刻</label>
            <input
              v-model="modalClockOut"
              type="time"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400"
            />
          </div>

          <!-- 休憩時間 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">休憩時間（分）</label>
            <input
              v-model.number="modalBreak"
              type="number"
              min="0"
              max="480"
              step="15"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400"
            />
          </div>

          <!-- エラー -->
          <div v-if="modalError" class="flex items-center gap-2 text-red-500 text-sm bg-red-50 rounded-lg px-3 py-2">
            <UIcon name="i-heroicons-exclamation-circle" class="w-4 h-4 flex-shrink-0" />
            {{ modalError }}
          </div>
        </div>

        <template #footer>
          <div class="flex justify-end gap-2">
            <UButton color="gray" variant="outline" @click="modalOpen = false">キャンセル</UButton>
            <UButton
              color="primary"
              :loading="modalLoading"
              icon="i-heroicons-check"
              @click="submitPastRecord"
            >登録</UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>
