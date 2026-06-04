<script setup lang="ts">
import type { YearlySummaryResponse } from "~/types/attendance"

const authStore = useAuthStore()
const attendanceStore = useAttendanceStore()
const notifStore = useNotificationsStore()
const toast = useToast()

if (!authStore.isLoggedIn) {
  await navigateTo("/login")
}

await attendanceStore.fetchToday()

// ライブ時刻
const now = ref(new Date())
let ticker: ReturnType<typeof setInterval>
onMounted(() => { ticker = setInterval(() => { now.value = new Date() }, 1000) })
onUnmounted(() => clearInterval(ticker))

// 打刻用時刻入力（現在時刻で初期化）
function currentTimeStr() {
  const d = new Date()
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`
}
const clockInTime = ref(currentTimeStr())
const clockOutTime = ref(currentTimeStr())

// 入力した "HH:MM" を今日の日付と組み合わせて ISO 文字列に変換
function toIso(timeStr: string): string {
  const [hour, minute] = timeStr.split(":").map(Number)
  const d = new Date()
  d.setHours(hour, minute, 0, 0)
  return d.toISOString()
}

// 退勤打刻専用: 計算結果が出勤時刻より前になる場合は翌日として扱う（夜間出勤対応）
function toIsoClockOut(timeStr: string, clockInIso?: string | null): string {
  const [hour, minute] = timeStr.split(":").map(Number)
  const d = new Date()
  d.setHours(hour, minute, 0, 0)
  if (clockInIso) {
    const utc = /[Z+]/.test(clockInIso) ? clockInIso : clockInIso + "Z"
    const clockInDt = new Date(utc)
    if (d < clockInDt) {
      d.setDate(d.getDate() + 1)
    }
  }
  return d.toISOString()
}

const statusLabel = computed(() => {
  switch (attendanceStore.today?.status) {
    case "PRESENT": return "出勤中"
    case "CLOSED": return "退勤済"
    case "CORRECTION_PENDING": return "修正申請中"
    case "CORRECTION_APPROVED": return "修正承認済"
    default: return "未出勤"
  }
})

const { roleTheme } = useRoleTheme()

const statusColor = computed(() => {
  switch (attendanceStore.today?.status) {
    case "PRESENT": return "green"
    case "CLOSED": return "blue"
    case "CORRECTION_PENDING": return "amber"
    case "CORRECTION_APPROVED": return "green"
    default: return "gray"
  }
})

const canClockIn = computed(() =>
  !attendanceStore.today || attendanceStore.today.status === "NOT_CLOCKED_IN"
)
const canClockOut = computed(() =>
  attendanceStore.today?.status === "PRESENT"
)
const canCorrect = computed(() =>
  attendanceStore.today?.status === "CLOSED" || attendanceStore.today?.status === "CORRECTION_PENDING"
)

// 出勤時刻の直接修正（出勤中のみ・承認不要）
const isFixingClockIn = ref(false)
const fixClockInTime = ref("")

function startFixClockIn() {
  fixClockInTime.value = fmt(attendanceStore.today?.record?.clock_in)
  isFixingClockIn.value = true
}

async function handleFixClockIn() {
  try {
    await attendanceStore.fixClockIn(toIso(fixClockInTime.value))
    toast.add({ title: `出勤時刻を ${fixClockInTime.value} に修正しました`, color: "green", icon: "i-heroicons-check-circle" })
    isFixingClockIn.value = false
  } catch {
    toast.add({ title: attendanceStore.error ?? "エラーが発生しました", color: "red", icon: "i-heroicons-exclamation-circle" })
  }
}

// 退勤時刻の直接修正（退勤済みのみ・承認不要）
const isFixingClockOut = ref(false)
const fixClockOutTime = ref("")

function startFixClockOut() {
  fixClockOutTime.value = fmt(attendanceStore.today?.record?.clock_out)
  isFixingClockOut.value = true
}

async function handleFixClockOut() {
  try {
    await attendanceStore.fixClockOut(toIsoClockOut(fixClockOutTime.value, attendanceStore.today?.record?.clock_in))
    toast.add({ title: `退勤時刻を ${fixClockOutTime.value} に修正しました`, color: "blue", icon: "i-heroicons-check-circle" })
    isFixingClockOut.value = false
  } catch {
    toast.add({ title: attendanceStore.error ?? "エラーが発生しました", color: "red", icon: "i-heroicons-exclamation-circle" })
  }
}

// 修正申請（承認が必要なケース: 両方まとめて修正・管理者レビュー）
const isEditing = ref(false)
const editClockIn = ref("")
const editClockOut = ref("")
const correctionNote = ref("")

function startEdit() {
  const rec = attendanceStore.today?.record
  editClockIn.value = rec?.clock_in ? fmt(rec.clock_in) : currentTimeStr()
  editClockOut.value = rec?.clock_out ? fmt(rec.clock_out) : currentTimeStr()
  correctionNote.value = ""
  isEditing.value = true
}

async function handleCorrection() {
  const rec = attendanceStore.today?.record
  if (!rec) return
  try {
    await attendanceStore.requestCorrection(rec.id, toIso(editClockIn.value), toIso(editClockOut.value), correctionNote.value)
    toast.add({ title: "修正申請を送信しました", color: "blue", icon: "i-heroicons-check-circle" })
    isEditing.value = false
  } catch {
    toast.add({ title: attendanceStore.error ?? "エラーが発生しました", color: "red", icon: "i-heroicons-exclamation-circle" })
  }
}

function fmt(iso: string | null | undefined) {
  if (!iso) return "--:--"
  // Append 'Z' if no timezone info so the string is treated as UTC, not local time
  const utc = /[Z+]/.test(iso) ? iso : iso + "Z"
  return new Date(utc).toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" })
}
function fmtMinutes(min: number) {
  const h = Math.floor(min / 60)
  const m = min % 60
  return h > 0 ? `${h}時間${m}分` : `${m}分`
}

async function handleClockIn() {
  try {
    await attendanceStore.clockIn(toIso(clockInTime.value))
    toast.add({ title: `${clockInTime.value} に出勤打刻しました`, color: "green", icon: "i-heroicons-check-circle" })
  } catch {
    toast.add({ title: attendanceStore.error ?? "エラーが発生しました", color: "red", icon: "i-heroicons-exclamation-circle" })
  }
}

async function handleClockOut() {
  try {
    await attendanceStore.clockOut(toIsoClockOut(clockOutTime.value, attendanceStore.today?.record?.clock_in))
    toast.add({ title: `${clockOutTime.value} に退勤打刻しました`, color: "blue", icon: "i-heroicons-check-circle" })
  } catch {
    toast.add({ title: attendanceStore.error ?? "エラーが発生しました", color: "red", icon: "i-heroicons-exclamation-circle" })
  }
}

// ── 年次残業グラフ（36協定チェック） ──────────────────────────
const yearlyData = ref<YearlySummaryResponse | null>(null)
const currentYear = new Date().getFullYear()
const CHART_MAX_MIN = 3600  // スケール上限 60h
const OT_LIMIT_MONTH = 2700 // 45h（月上限）
const OT_LIMIT_YEAR  = 21600 // 360h（年上限）
const MONTH_LABELS = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']

onMounted(async () => {
  try { yearlyData.value = await attendanceStore.fetchYearly(currentYear) } catch { /* non-critical */ }
})

function barHeight(min: number) { return Math.min((min / CHART_MAX_MIN) * 100, 100) }
function barColor(min: number)  {
  if (min >= OT_LIMIT_MONTH) return 'bg-red-500'
  if (min >= 1800)           return 'bg-amber-400'
  return 'bg-brand-400'
}
function fmtH(min: number) { return parseFloat((min / 60).toFixed(1)) }

const monthAlerts = computed(() =>
  (yearlyData.value?.months ?? [])
    .filter(m => m.overtime_minutes >= OT_LIMIT_MONTH)
    .map(m => `${Number(m.month.slice(5))}月`)
)
const annualOtMin  = computed(() => yearlyData.value?.total_overtime_minutes ?? 0)
const annualOtH    = computed(() => fmtH(annualOtMin.value))
const annualOtPct  = computed(() => Math.min((annualOtMin.value / OT_LIMIT_YEAR) * 100, 100))
</script>

<template>
  <div :class="['min-h-screen', roleTheme.pageBg]">
    <!-- ヘッダー -->
    <header :class="[roleTheme.header, 'shadow-lg']">
      <div class="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center shadow">
            <UIcon name="i-heroicons-clock" class="w-5 h-5 text-white" />
          </div>
          <span class="text-lg font-bold text-white">AttendEase</span>
        </div>
        <div class="flex items-center gap-3">
          <span :class="['text-sm hidden sm:block', roleTheme.sub1]">{{ authStore.user?.name }} さん</span>
          <!-- 通知ベル -->
          <NuxtLink to="/notifications" class="relative">
            <UButton variant="ghost" size="sm" icon="i-heroicons-bell" class="!text-white hover:!bg-white/20 rounded-lg" />
            <span
              v-if="notifStore.unreadCount > 0"
              class="absolute -top-1 -right-1 min-w-[18px] h-[18px] bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center px-1"
            >{{ notifStore.unreadCount > 99 ? '99+' : notifStore.unreadCount }}</span>
          </NuxtLink>
          <!-- プロフィール -->
          <NuxtLink to="/profile">
            <UButton variant="ghost" size="sm" icon="i-heroicons-user-circle" class="!text-white hover:!bg-white/20 rounded-lg" />
          </NuxtLink>
          <UButton
            variant="ghost" size="sm"
            icon="i-heroicons-arrow-right-on-rectangle"
            class="!bg-red-500 !text-white hover:!bg-red-600 transition-all duration-200 font-medium rounded-lg"
            @click="authStore.logout()"
          >ログアウト</UButton>
        </div>
      </div>
    </header>

    <main class="max-w-5xl mx-auto px-6 py-10 space-y-6">
      <!-- ウェルカムバナー -->
      <div :class="[roleTheme.banner, 'rounded-2xl p-8 text-white shadow-lg']">
        <p :class="[roleTheme.sub1, 'text-sm mb-1']">おかえりなさい</p>
        <h1 class="text-2xl font-bold mb-2">{{ authStore.user?.name }} さん</h1>
        <p :class="[roleTheme.sub2, 'text-sm']">
          {{ now.toLocaleDateString("ja-JP", { year: "numeric", month: "long", day: "numeric", weekday: "long" }) }}
          &nbsp;
          <span class="font-mono text-base text-white">{{ now.toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit", second: "2-digit" }) }}</span>
        </p>
      </div>

      <!-- タイムカード + 年次グラフ（2カラム） -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">

      <!-- タイムカード -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-base font-semibold text-gray-800">本日の勤怠</h2>
          <UBadge :color="statusColor" variant="subtle" size="lg">{{ statusLabel }}</UBadge>
        </div>

        <!-- タイムカード本体 -->
        <div class="grid grid-cols-2 gap-4 mb-5">
          <!-- 出勤パネル -->
          <div class="bg-green-50 border border-green-100 rounded-xl p-4 flex flex-col items-center gap-3">
            <p class="text-xs font-semibold text-green-700 tracking-wide uppercase">出勤時刻</p>

            <!-- 未出勤: 時刻入力 + 出勤ボタン -->
            <template v-if="canClockIn">
              <input
                v-model="clockInTime"
                type="time"
                class="w-full text-center text-3xl font-bold font-mono text-green-800 bg-white border border-green-200 rounded-lg px-2 py-2 focus:outline-none focus:ring-2 focus:ring-green-400 cursor-pointer"
              />
              <UButton color="green" size="sm" icon="i-heroicons-arrow-right-circle"
                class="w-full justify-center font-semibold"
                :loading="attendanceStore.isLoading" :disabled="attendanceStore.isLoading"
                @click="handleClockIn">出勤する</UButton>
            </template>

            <!-- 出勤中: 時刻表示 + 修正ボタン -->
            <template v-else-if="canClockOut">
              <template v-if="!isFixingClockIn">
                <p class="text-3xl font-bold text-green-800 font-mono py-1">
                  {{ fmt(attendanceStore.today?.record?.clock_in) }}
                </p>
                <UButton color="green" variant="soft" size="xs" icon="i-heroicons-pencil-square"
                  @click="startFixClockIn">時刻を修正</UButton>
              </template>
              <template v-else>
                <input v-model="fixClockInTime" type="time"
                  class="w-full text-center text-2xl font-bold font-mono text-green-800 bg-white border border-green-300 rounded-lg px-2 py-2 focus:outline-none focus:ring-2 focus:ring-green-400" />
                <div class="flex gap-2 w-full">
                  <UButton color="gray" variant="soft" size="xs" class="flex-1 justify-center"
                    @click="isFixingClockIn = false">キャンセル</UButton>
                  <UButton color="green" size="xs" icon="i-heroicons-check" class="flex-1 justify-center"
                    :loading="attendanceStore.isLoading" :disabled="attendanceStore.isLoading"
                    @click="handleFixClockIn">修正する</UButton>
                </div>
              </template>
            </template>

            <!-- 退勤済: 時刻表示 + 修正ボタン -->
            <template v-else-if="attendanceStore.today?.status === 'CLOSED'">
              <template v-if="!isFixingClockIn">
                <p class="text-3xl font-bold text-green-800 font-mono py-1">
                  {{ fmt(attendanceStore.today?.record?.clock_in) }}
                </p>
                <UButton color="green" variant="soft" size="xs" icon="i-heroicons-pencil-square"
                  @click="startFixClockIn">時刻を修正</UButton>
              </template>
              <template v-else>
                <input v-model="fixClockInTime" type="time"
                  class="w-full text-center text-2xl font-bold font-mono text-green-800 bg-white border border-green-300 rounded-lg px-2 py-2 focus:outline-none focus:ring-2 focus:ring-green-400" />
                <div class="flex gap-2 w-full">
                  <UButton color="gray" variant="soft" size="xs" class="flex-1 justify-center"
                    @click="isFixingClockIn = false">キャンセル</UButton>
                  <UButton color="green" size="xs" icon="i-heroicons-check" class="flex-1 justify-center"
                    :loading="attendanceStore.isLoading" :disabled="attendanceStore.isLoading"
                    @click="handleFixClockIn">修正する</UButton>
                </div>
              </template>
            </template>

            <!-- 申請中など: 読み取り専用 -->
            <p v-else class="text-3xl font-bold text-green-800 font-mono py-2">
              {{ fmt(attendanceStore.today?.record?.clock_in) }}
            </p>
          </div>

          <!-- 退勤パネル -->
          <div class="bg-orange-50 border border-orange-100 rounded-xl p-4 flex flex-col items-center gap-3">
            <p class="text-xs font-semibold text-orange-700 tracking-wide uppercase">退勤時刻</p>

            <!-- 出勤中: 時刻入力 + 退勤ボタン -->
            <template v-if="canClockOut">
              <input
                v-model="clockOutTime"
                type="time"
                class="w-full text-center text-3xl font-bold font-mono text-orange-800 bg-white border border-orange-200 rounded-lg px-2 py-2 focus:outline-none focus:ring-2 focus:ring-orange-400 cursor-pointer"
              />
              <UButton color="orange" size="sm" icon="i-heroicons-arrow-left-circle"
                class="w-full justify-center font-semibold"
                :loading="attendanceStore.isLoading" :disabled="attendanceStore.isLoading"
                @click="handleClockOut">退勤する</UButton>
            </template>

            <!-- 退勤済み: 時刻表示 + 修正ボタン -->
            <template v-else-if="attendanceStore.today?.status === 'CLOSED'">
              <template v-if="!isFixingClockOut">
                <p class="text-3xl font-bold text-orange-800 font-mono py-1">
                  {{ fmt(attendanceStore.today?.record?.clock_out) }}
                </p>
                <UButton color="orange" variant="soft" size="xs" icon="i-heroicons-pencil-square"
                  @click="startFixClockOut">時刻を修正</UButton>
              </template>
              <template v-else>
                <input v-model="fixClockOutTime" type="time"
                  class="w-full text-center text-2xl font-bold font-mono text-orange-800 bg-white border border-orange-300 rounded-lg px-2 py-2 focus:outline-none focus:ring-2 focus:ring-orange-400" />
                <div class="flex gap-2 w-full">
                  <UButton color="gray" variant="soft" size="xs" class="flex-1 justify-center"
                    @click="isFixingClockOut = false">キャンセル</UButton>
                  <UButton color="orange" size="xs" icon="i-heroicons-check" class="flex-1 justify-center"
                    :loading="attendanceStore.isLoading" :disabled="attendanceStore.isLoading"
                    @click="handleFixClockOut">修正する</UButton>
                </div>
              </template>
            </template>

            <!-- 未出勤・申請中: 読み取り専用 -->
            <p v-else class="text-3xl font-bold text-orange-800 font-mono py-2">
              {{ fmt(attendanceStore.today?.record?.clock_out) ?? "--:--" }}
            </p>
          </div>
        </div>

        <!-- 入力ヒント（打刻前のみ） -->
        <p v-if="canClockIn || canClockOut" class="text-xs text-gray-400 text-center mb-4">
          時刻を変更してからボタンを押してください
        </p>

        <!-- 修正申請（出勤・退勤両方まとめて修正 / 管理者承認が必要） -->
        <template v-if="canCorrect">
          <div v-if="!isEditing" class="flex justify-center mb-4">
            <UButton color="amber" variant="soft" size="sm" icon="i-heroicons-clipboard-document-check"
              @click="startEdit">出退勤を両方修正申請する</UButton>
          </div>
          <div v-else class="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4 space-y-3">
            <p class="text-xs font-semibold text-amber-700">修正申請（管理者承認が必要）</p>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs text-gray-500 mb-1 block">出勤時刻</label>
                <input v-model="editClockIn" type="time"
                  class="w-full text-center text-lg font-mono bg-white border border-amber-300 rounded-lg px-2 py-2 focus:outline-none focus:ring-2 focus:ring-amber-400" />
              </div>
              <div>
                <label class="text-xs text-gray-500 mb-1 block">退勤時刻</label>
                <input v-model="editClockOut" type="time"
                  class="w-full text-center text-lg font-mono bg-white border border-amber-300 rounded-lg px-2 py-2 focus:outline-none focus:ring-2 focus:ring-amber-400" />
              </div>
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">修正理由（必須）</label>
              <input v-model="correctionNote" type="text" placeholder="例: 打刻漏れのため"
                class="w-full bg-white border border-amber-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400" />
            </div>
            <div class="flex gap-2 justify-end">
              <UButton color="gray" variant="soft" size="sm" @click="isEditing = false">キャンセル</UButton>
              <UButton color="amber" size="sm" icon="i-heroicons-paper-airplane"
                :loading="attendanceStore.isLoading"
                :disabled="attendanceStore.isLoading || !correctionNote.trim()"
                @click="handleCorrection">申請する</UButton>
            </div>
          </div>
        </template>

        <!-- 労働時間（退勤済のみ表示） -->
        <div
          v-if="attendanceStore.today?.record?.work_minutes != null"
          class="bg-brand-50 rounded-xl p-4 text-center"
        >
          <p class="text-xs text-brand-700 font-medium mb-1">労働時間</p>
          <p class="text-xl font-bold text-brand-800">
            {{ fmtMinutes(attendanceStore.today!.record!.work_minutes!) }}
          </p>
        </div>
      </div><!-- /タイムカード -->

      <!-- 年次残業サマリー（右カラム） -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-chart-bar" class="w-5 h-5 text-brand-500" />
            <h2 class="text-base font-semibold text-gray-800">{{ currentYear }}年 残業サマリー</h2>
          </div>
          <span class="text-[10px] text-gray-400 bg-gray-100 rounded px-2 py-0.5">36協定 月45h / 年360h</span>
        </div>

        <!-- アラート -->
        <div v-if="monthAlerts.length > 0" class="mb-4 bg-red-50 border border-red-200 rounded-xl px-4 py-3 flex items-start gap-2">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
          <div>
            <p class="text-xs font-bold text-red-700">⚠ 36協定上限超過の疑い</p>
            <p class="text-xs text-red-600 mt-0.5">{{ monthAlerts.join('・') }} に月45hを超える残業があります</p>
          </div>
        </div>
        <div v-else-if="annualOtH >= 300" class="mb-4 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 flex items-start gap-2">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
          <p class="text-xs text-amber-700">年間残業 {{ annualOtH }}h — 年360h上限に近づいています</p>
        </div>

        <div v-if="yearlyData">
          <!-- 棒グラフ -->
          <div class="relative flex items-end gap-[3px] h-36 mb-1 px-1">
            <!-- 45h 基準線 -->
            <div
              class="absolute left-0 right-0 border-t-2 border-dashed border-red-300 pointer-events-none z-10"
              :style="{ bottom: (OT_LIMIT_MONTH / CHART_MAX_MIN * 100) + '%' }"
            >
              <span class="absolute -right-1 -top-4 text-[9px] text-red-400 font-semibold whitespace-nowrap">45h</span>
            </div>
            <!-- 各月バー -->
            <div
              v-for="(m, i) in yearlyData.months"
              :key="m.month"
              class="flex-1 relative flex flex-col justify-end h-full group"
            >
              <!-- tooltip -->
              <div class="absolute bottom-full mb-1 left-1/2 -translate-x-1/2 bg-gray-800 text-white text-[9px] rounded px-1.5 py-0.5 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity z-20 pointer-events-none">
                {{ fmtH(m.overtime_minutes) }}h
              </div>
              <div
                class="w-full rounded-t-sm transition-all duration-500"
                :class="barColor(m.overtime_minutes)"
                :style="{ height: Math.max(barHeight(m.overtime_minutes), m.overtime_minutes > 0 ? 2 : 0) + '%' }"
              />
            </div>
          </div>

          <!-- 月ラベル -->
          <div class="flex gap-[3px] px-1 mb-5">
            <div v-for="label in MONTH_LABELS" :key="label" class="flex-1 text-center text-[9px] text-gray-400">
              {{ label }}
            </div>
          </div>

          <!-- 凡例 -->
          <div class="flex gap-4 text-[10px] text-gray-500 mb-4">
            <div class="flex items-center gap-1"><div class="w-2.5 h-2.5 rounded-sm bg-brand-400"></div>通常</div>
            <div class="flex items-center gap-1"><div class="w-2.5 h-2.5 rounded-sm bg-amber-400"></div>注意（30h+）</div>
            <div class="flex items-center gap-1"><div class="w-2.5 h-2.5 rounded-sm bg-red-500"></div>上限超（45h+）</div>
          </div>

          <!-- 年間合計 -->
          <div class="bg-gray-50 rounded-xl p-4 space-y-2">
            <div class="flex justify-between items-center">
              <span class="text-xs text-gray-500">年間残業合計</span>
              <span
                class="text-sm font-bold"
                :class="annualOtH >= 360 ? 'text-red-600' : annualOtH >= 300 ? 'text-amber-600' : 'text-brand-700'"
              >{{ annualOtH }}h <span class="text-xs font-normal text-gray-400">/ 360h</span></span>
            </div>
            <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-700"
                :class="annualOtH >= 360 ? 'bg-red-500' : annualOtH >= 300 ? 'bg-amber-400' : 'bg-brand-500'"
                :style="{ width: annualOtPct + '%' }"
              />
            </div>
            <div class="flex justify-between text-[9px] text-gray-400">
              <span>0h</span><span>180h</span><span>360h</span>
            </div>
          </div>
        </div>

        <!-- ローディング -->
        <div v-else class="flex items-center justify-center h-40">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 text-gray-300 animate-spin" />
        </div>
      </div><!-- /年次グラフ -->

      </div><!-- /2カラムグリッド -->

      <!-- クイックリンク -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <NuxtLink to="/attendance" class="block">
          <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex items-center gap-4 hover:shadow-md transition-shadow cursor-pointer">
            <div class="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center flex-shrink-0">
              <UIcon name="i-heroicons-calendar-days" class="w-7 h-7 text-purple-600" />
            </div>
            <div>
              <p class="font-semibold text-gray-800">勤怠一覧</p>
              <p class="text-sm text-gray-500">月次の出退勤記録を確認する</p>
            </div>
          </div>
        </NuxtLink>

        <NuxtLink to="/leaves" class="block">
          <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex items-center gap-4 hover:shadow-md transition-shadow cursor-pointer">
            <div class="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center flex-shrink-0">
              <UIcon name="i-heroicons-calendar" class="w-7 h-7 text-green-600" />
            </div>
            <div>
              <p class="font-semibold text-gray-800">休暇申請</p>
              <p class="text-sm text-gray-500">休暇の申請・履歴を確認する</p>
            </div>
          </div>
        </NuxtLink>

        <NuxtLink to="/overtime" class="block">
          <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex items-center gap-4 hover:shadow-md transition-shadow cursor-pointer">
            <div class="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center flex-shrink-0">
              <UIcon name="i-heroicons-clock" class="w-7 h-7 text-orange-600" />
            </div>
            <div>
              <p class="font-semibold text-gray-800">残業申請</p>
              <p class="text-sm text-gray-500">残業の申請・履歴を確認する</p>
            </div>
          </div>
        </NuxtLink>

        <NuxtLink v-if="['MANAGER', 'ADMIN'].includes(authStore.user?.role ?? '')" to="/reports" class="block">
          <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex items-center gap-4 hover:shadow-md transition-shadow cursor-pointer">
            <div class="w-12 h-12 rounded-xl bg-brand-100 flex items-center justify-center flex-shrink-0">
              <UIcon name="i-heroicons-chart-bar" class="w-7 h-7 text-brand-600" />
            </div>
            <div>
              <p class="font-semibold text-gray-800">勤怠レポート</p>
              <p class="text-sm text-gray-500">月次サマリー・CSV出力</p>
            </div>
          </div>
        </NuxtLink>
        <div v-else class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex items-center gap-4 opacity-40">
          <div class="w-12 h-12 rounded-xl bg-brand-100 flex items-center justify-center flex-shrink-0">
            <UIcon name="i-heroicons-chart-bar" class="w-7 h-7 text-brand-600" />
          </div>
          <div>
            <p class="font-semibold text-gray-800">勤怠レポート</p>
            <p class="text-sm text-gray-500">管理者・マネージャー向け</p>
          </div>
        </div>

        <NuxtLink to="/notifications" class="block">
          <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex items-center gap-4 hover:shadow-md transition-shadow cursor-pointer">
            <div class="relative w-12 h-12 rounded-xl bg-brand-100 flex items-center justify-center flex-shrink-0">
              <UIcon name="i-heroicons-bell" class="w-7 h-7 text-brand-600" />
              <span
                v-if="notifStore.unreadCount > 0"
                class="absolute -top-1 -right-1 min-w-[18px] h-[18px] bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center px-1"
              >{{ notifStore.unreadCount }}</span>
            </div>
            <div>
              <p class="font-semibold text-gray-800">通知</p>
              <p class="text-sm text-gray-500">申請・承認の通知を確認する</p>
            </div>
          </div>
        </NuxtLink>

        <NuxtLink to="/profile" class="block">
          <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex items-center gap-4 hover:shadow-md transition-shadow cursor-pointer">
            <div class="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center flex-shrink-0">
              <UIcon name="i-heroicons-user-circle" class="w-7 h-7 text-gray-600" />
            </div>
            <div>
              <p class="font-semibold text-gray-800">プロフィール設定</p>
              <p class="text-sm text-gray-500">氏名・メール・パスワードを変更する</p>
            </div>
          </div>
        </NuxtLink>
      </div>

      <!-- 承認担当者・管理者メニュー -->
      <div v-if="['MANAGER', 'ADMIN'].includes(authStore.user?.role ?? '')" class="bg-white rounded-xl p-6 shadow-sm border border-orange-200">
        <div class="flex items-center gap-2 mb-4">
          <UIcon name="i-heroicons-check-badge" class="w-5 h-5 text-orange-500" />
          <h2 class="font-semibold text-gray-800">承認メニュー</h2>
        </div>
        <div class="flex gap-2 flex-wrap">
          <UButton color="orange" variant="soft" icon="i-heroicons-clipboard-document-check" to="/leaves/approve">
            休暇承認
          </UButton>
          <UButton color="orange" variant="soft" icon="i-heroicons-clock" to="/overtime/approve">
            残業承認
          </UButton>
          <UButton color="indigo" variant="soft" icon="i-heroicons-chart-bar" to="/reports">
            勤怠レポート
          </UButton>
        </div>
      </div>

      <!-- 管理者メニュー -->
      <div v-if="authStore.user?.role === 'ADMIN'" class="bg-white rounded-xl p-6 shadow-sm border border-amber-200">
        <div class="flex items-center gap-2 mb-4">
          <UIcon name="i-heroicons-shield-check" class="w-5 h-5 text-amber-500" />
          <h2 class="font-semibold text-gray-800">管理者メニュー</h2>
        </div>
        <div class="flex gap-2 flex-wrap">
          <UButton color="amber" variant="outline" icon="i-heroicons-user-plus" to="/admin/users">
            ユーザー管理
          </UButton>
          <UButton color="amber" variant="outline" icon="i-heroicons-calendar-days" to="/admin/leave-balances">
            有給残日数管理
          </UButton>
        </div>
      </div>
    </main>
  </div>
</template>
