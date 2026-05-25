<script setup lang="ts">
definePageMeta({ middleware: ["manager-or-admin"] })

interface UserMonthlySummary {
  user_id: number
  employee_id: string
  name: string
  work_days: number
  total_work_minutes: number
  total_overtime_minutes: number
  leave_days: number
}

interface MonthlySummaryResponse {
  month: string
  users: UserMonthlySummary[]
  total_work_minutes: number
  total_overtime_minutes: number
}

const config = useRuntimeConfig()
const authStore = useAuthStore()

function currentMonthStr() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`
}

const selectedMonth = ref(currentMonthStr())
const summary = ref<MonthlySummaryResponse | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)
const downloadingCsv = ref<"attendance" | "leaves" | "overtime" | null>(null)

function authHeaders() {
  return { Authorization: `Bearer ${authStore.token}` }
}

async function fetchSummary() {
  isLoading.value = true
  error.value = null
  try {
    summary.value = await $fetch<MonthlySummaryResponse>(
      `${config.public.apiBase}/api/v1/reports/summary?month=${selectedMonth.value}`,
      { headers: authHeaders() },
    )
  } catch {
    error.value = "サマリーの取得に失敗しました"
  } finally {
    isLoading.value = false
  }
}

async function downloadCsv(type: "attendance" | "leaves" | "overtime") {
  downloadingCsv.value = type
  try {
    const res = await fetch(
      `${config.public.apiBase}/api/v1/reports/${type}/csv?month=${selectedMonth.value}`,
      { headers: authHeaders() },
    )
    if (!res.ok) throw new Error("Download failed")
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `${type}_${selectedMonth.value}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    error.value = "CSVのダウンロードに失敗しました"
  } finally {
    downloadingCsv.value = null
  }
}

function fmtMinutes(m: number) {
  const h = Math.floor(m / 60)
  const min = m % 60
  return min > 0 ? `${h}時間${min}分` : `${h}時間`
}

function otColor(m: number) {
  if (m >= 2700) return "text-red-600 font-bold"
  if (m >= 1800) return "text-amber-600 font-semibold"
  return "text-gray-700"
}

await fetchSummary()
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
    <!-- ヘッダー -->
    <header class="bg-gradient-to-r from-blue-700 to-indigo-800 shadow-lg">
      <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <NuxtLink to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div class="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center shadow">
              <UIcon name="i-heroicons-clock" class="w-5 h-5 text-white" />
            </div>
            <span class="text-lg font-bold text-white">AttendEase</span>
          </NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-4 h-4 text-blue-300" />
          <span class="text-sm text-blue-100 font-medium">勤怠レポート</span>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-blue-100 hidden sm:block">{{ authStore.user?.name }} さん</span>
          <UButton
            variant="ghost" size="sm"
            icon="i-heroicons-arrow-right-on-rectangle"
            class="!bg-red-500 !text-white hover:!bg-red-600 transition-all duration-200 font-medium rounded-lg"
            @click="authStore.logout()"
          >ログアウト</UButton>
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-6 py-10 space-y-6">
      <!-- タイトル + 月選択 -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div class="flex items-center gap-2">
          <UIcon name="i-heroicons-chart-bar" class="w-6 h-6 text-indigo-600" />
          <h1 class="text-xl font-bold text-gray-800">月次勤怠レポート</h1>
        </div>
        <div class="flex items-center gap-3">
          <input
            v-model="selectedMonth"
            type="month"
            class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 bg-white"
            @change="fetchSummary"
          />
          <UButton
            color="indigo"
            variant="soft"
            icon="i-heroicons-arrow-path"
            :loading="isLoading"
            @click="fetchSummary"
          >更新</UButton>
        </div>
      </div>

      <!-- エラー -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl px-5 py-4 text-sm text-red-700">
        {{ error }}
      </div>

      <!-- CSV ダウンロードボタン -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-center gap-2 mb-4">
          <UIcon name="i-heroicons-arrow-down-tray" class="w-5 h-5 text-gray-500" />
          <h2 class="font-semibold text-gray-800">CSV ダウンロード</h2>
          <span class="text-sm text-gray-400 ml-1">— {{ selectedMonth }} 分</span>
        </div>
        <div class="flex flex-wrap gap-3">
          <UButton
            color="blue"
            variant="soft"
            icon="i-heroicons-calendar-days"
            :loading="downloadingCsv === 'attendance'"
            :disabled="!!downloadingCsv"
            @click="downloadCsv('attendance')"
          >勤怠データ CSV</UButton>
          <UButton
            color="green"
            variant="soft"
            icon="i-heroicons-calendar"
            :loading="downloadingCsv === 'leaves'"
            :disabled="!!downloadingCsv"
            @click="downloadCsv('leaves')"
          >休暇申請 CSV</UButton>
          <UButton
            color="orange"
            variant="soft"
            icon="i-heroicons-clock"
            :loading="downloadingCsv === 'overtime'"
            :disabled="!!downloadingCsv"
            @click="downloadCsv('overtime')"
          >残業申請 CSV</UButton>
        </div>
      </div>

      <!-- ローディング -->
      <div v-if="isLoading && !summary" class="flex items-center justify-center py-20">
        <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 text-gray-400 animate-spin" />
      </div>

      <!-- サマリーテーブル -->
      <div v-else-if="summary" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 class="font-semibold text-gray-800">ユーザー別月次サマリー</h2>
          <UBadge color="indigo" variant="subtle">{{ summary.users.length }}名</UBadge>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">社員ID</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">氏名</th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">出勤日数</th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">実働時間</th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">残業時間</th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">有給取得</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr
                v-for="u in summary.users"
                :key="u.user_id"
                class="hover:bg-gray-50 transition-colors"
              >
                <td class="px-4 py-3 text-gray-500 font-mono text-xs">{{ u.employee_id }}</td>
                <td class="px-4 py-3 font-medium text-gray-800">{{ u.name }}</td>
                <td class="px-4 py-3 text-right text-gray-700">{{ u.work_days }}日</td>
                <td class="px-4 py-3 text-right text-gray-700">{{ fmtMinutes(u.total_work_minutes) }}</td>
                <td class="px-4 py-3 text-right" :class="otColor(u.total_overtime_minutes)">
                  <div class="flex items-center justify-end gap-1">
                    <UIcon
                      v-if="u.total_overtime_minutes >= 2700"
                      name="i-heroicons-exclamation-triangle"
                      class="w-3.5 h-3.5 text-red-500"
                    />
                    {{ fmtMinutes(u.total_overtime_minutes) }}
                  </div>
                </td>
                <td class="px-4 py-3 text-right text-gray-700">{{ u.leave_days }}日</td>
              </tr>

              <!-- 合計行 -->
              <tr class="bg-indigo-50 font-semibold border-t-2 border-indigo-100">
                <td class="px-4 py-3 text-indigo-700" colspan="2">合計</td>
                <td class="px-4 py-3 text-right text-indigo-700">
                  {{ summary.users.reduce((s, u) => s + u.work_days, 0) }}日
                </td>
                <td class="px-4 py-3 text-right text-indigo-700">{{ fmtMinutes(summary.total_work_minutes) }}</td>
                <td class="px-4 py-3 text-right text-indigo-700">{{ fmtMinutes(summary.total_overtime_minutes) }}</td>
                <td class="px-4 py-3 text-right text-indigo-700">
                  {{ summary.users.reduce((s, u) => s + u.leave_days, 0) }}日
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 空状態 -->
      <div v-else-if="!isLoading" class="bg-white rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center py-20 gap-3">
        <UIcon name="i-heroicons-document-chart-bar" class="w-12 h-12 text-gray-300" />
        <p class="text-gray-500">データがありません</p>
      </div>
    </main>
  </div>
</template>
