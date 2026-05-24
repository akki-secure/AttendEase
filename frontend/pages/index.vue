<script setup lang="ts">
const authStore = useAuthStore()
const attendanceStore = useAttendanceStore()
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

const statusLabel = computed(() => {
  switch (attendanceStore.today?.status) {
    case "PRESENT": return "出勤中"
    case "CLOSED": return "退勤済"
    case "CORRECTION_PENDING": return "修正申請中"
    case "CORRECTION_APPROVED": return "修正承認済"
    default: return "未出勤"
  }
})

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

// 修正申請モード
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
  return new Date(iso).toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" })
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
    await attendanceStore.clockOut(toIso(clockOutTime.value))
    toast.add({ title: `${clockOutTime.value} に退勤打刻しました`, color: "blue", icon: "i-heroicons-check-circle" })
  } catch {
    toast.add({ title: attendanceStore.error ?? "エラーが発生しました", color: "red", icon: "i-heroicons-exclamation-circle" })
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
    <!-- ヘッダー -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center shadow">
            <UIcon name="i-heroicons-clock" class="w-5 h-5 text-white" />
          </div>
          <span class="text-lg font-bold text-gray-900">AttendEase</span>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-gray-500 hidden sm:block">{{ authStore.user?.name }} さん</span>
          <UButton
            color="gray" variant="soft" size="sm"
            icon="i-heroicons-arrow-right-on-rectangle"
            @click="authStore.logout()"
          >ログアウト</UButton>
        </div>
      </div>
    </header>

    <main class="max-w-5xl mx-auto px-6 py-10 space-y-6">
      <!-- ウェルカムバナー -->
      <div class="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-8 text-white shadow-lg">
        <p class="text-blue-100 text-sm mb-1">おかえりなさい</p>
        <h1 class="text-2xl font-bold mb-2">{{ authStore.user?.name }} さん</h1>
        <p class="text-blue-200 text-sm">
          {{ now.toLocaleDateString("ja-JP", { year: "numeric", month: "long", day: "numeric", weekday: "long" }) }}
          &nbsp;
          <span class="font-mono text-base text-white">{{ now.toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit", second: "2-digit" }) }}</span>
        </p>
      </div>

      <!-- タイムカード -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-base font-semibold text-gray-800">本日の勤怠</h2>
          <UBadge :color="statusColor" variant="subtle" size="lg">{{ statusLabel }}</UBadge>
        </div>

        <!-- タイムカード本体 -->
        <div class="grid grid-cols-2 gap-4 mb-5">
          <!-- 出勤 -->
          <div class="bg-green-50 border border-green-100 rounded-xl p-4 flex flex-col items-center gap-3">
            <p class="text-xs font-semibold text-green-700 tracking-wide uppercase">出勤時刻</p>
            <template v-if="canClockIn">
              <!-- 時刻入力 -->
              <input
                v-model="clockInTime"
                type="time"
                class="w-full text-center text-3xl font-bold font-mono text-green-800 bg-white border border-green-200 rounded-lg px-2 py-2 focus:outline-none focus:ring-2 focus:ring-green-400 cursor-pointer"
              />
              <UButton
                color="green"
                size="sm"
                icon="i-heroicons-arrow-right-circle"
                class="w-full justify-center font-semibold"
                :loading="attendanceStore.isLoading"
                :disabled="attendanceStore.isLoading"
                @click="handleClockIn"
              >
                出勤する
              </UButton>
            </template>
            <p v-else class="text-3xl font-bold text-green-800 font-mono py-2">
              {{ fmt(attendanceStore.today?.record?.clock_in) }}
            </p>
          </div>

          <!-- 退勤 -->
          <div class="bg-orange-50 border border-orange-100 rounded-xl p-4 flex flex-col items-center gap-3">
            <p class="text-xs font-semibold text-orange-700 tracking-wide uppercase">退勤時刻</p>
            <template v-if="canClockOut">
              <!-- 時刻入力 -->
              <input
                v-model="clockOutTime"
                type="time"
                class="w-full text-center text-3xl font-bold font-mono text-orange-800 bg-white border border-orange-200 rounded-lg px-2 py-2 focus:outline-none focus:ring-2 focus:ring-orange-400 cursor-pointer"
              />
              <UButton
                color="orange"
                size="sm"
                icon="i-heroicons-arrow-left-circle"
                class="w-full justify-center font-semibold"
                :loading="attendanceStore.isLoading"
                :disabled="attendanceStore.isLoading"
                @click="handleClockOut"
              >
                退勤する
              </UButton>
            </template>
            <p v-else class="text-3xl font-bold text-orange-800 font-mono py-2">
              {{ fmt(attendanceStore.today?.record?.clock_out) }}
            </p>
          </div>
        </div>

        <!-- 入力ヒント（打刻前のみ） -->
        <p v-if="canClockIn || canClockOut" class="text-xs text-gray-400 text-center mb-4">
          時刻を変更してからボタンを押してください
        </p>

        <!-- 修正申請フォーム -->
        <template v-if="canCorrect">
          <div v-if="!isEditing" class="flex justify-center mb-4">
            <UButton
              color="amber" variant="soft" size="sm"
              icon="i-heroicons-pencil-square"
              @click="startEdit"
            >時刻を修正する</UButton>
          </div>
          <div v-else class="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4 space-y-3">
            <p class="text-xs font-semibold text-amber-700">修正申請</p>
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
              <UButton
                color="amber" size="sm"
                icon="i-heroicons-paper-airplane"
                :loading="attendanceStore.isLoading"
                :disabled="attendanceStore.isLoading || !correctionNote.trim()"
                @click="handleCorrection"
              >申請する</UButton>
            </div>
          </div>
        </template>

        <!-- 労働時間（退勤済のみ表示） -->
        <div
          v-if="attendanceStore.today?.record?.work_minutes != null"
          class="bg-blue-50 rounded-xl p-4 text-center"
        >
          <p class="text-xs text-blue-700 font-medium mb-1">労働時間</p>
          <p class="text-xl font-bold text-blue-800">
            {{ fmtMinutes(attendanceStore.today!.record!.work_minutes!) }}
          </p>
        </div>
      </div>

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

        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex items-center gap-4 opacity-50">
          <div class="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center flex-shrink-0">
            <UIcon name="i-heroicons-chart-bar" class="w-7 h-7 text-blue-600" />
          </div>
          <div>
            <p class="font-semibold text-gray-800">勤怠レポート</p>
            <p class="text-sm text-gray-500">近日公開予定</p>
          </div>
        </div>
      </div>

      <!-- 承認担当者・管理者メニュー -->
      <div v-if="['MANAGER', 'ADMIN'].includes(authStore.user?.role ?? '')" class="bg-white rounded-xl p-6 shadow-sm border border-orange-200">
        <div class="flex items-center gap-2 mb-4">
          <UIcon name="i-heroicons-check-badge" class="w-5 h-5 text-orange-500" />
          <h2 class="font-semibold text-gray-800">承認メニュー</h2>
        </div>
        <UButton color="orange" variant="soft" icon="i-heroicons-clipboard-document-check" to="/leaves/approve">
          休暇承認
        </UButton>
      </div>

      <!-- 管理者メニュー -->
      <div v-if="authStore.user?.role === 'ADMIN'" class="bg-white rounded-xl p-6 shadow-sm border border-amber-200">
        <div class="flex items-center gap-2 mb-4">
          <UIcon name="i-heroicons-shield-check" class="w-5 h-5 text-amber-500" />
          <h2 class="font-semibold text-gray-800">管理者メニュー</h2>
        </div>
        <div class="flex gap-2 flex-wrap">
          <UButton color="amber" variant="soft" icon="i-heroicons-user-plus" to="/admin/users">
            ユーザー管理
          </UButton>
          <UButton color="amber" variant="soft" icon="i-heroicons-calendar-days" to="/admin/leave-balances">
            有給残日数管理
          </UButton>
        </div>
      </div>
    </main>
  </div>
</template>
