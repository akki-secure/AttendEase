<script setup lang="ts">
import type { OvertimeCreatePayload } from "~/types/overtime"

const authStore = useAuthStore()
const overtimeStore = useOvertimeStore()

if (!authStore.isLoggedIn) {
  await navigateTo("/login")
}

const currentYear = new Date().getFullYear()
const currentMonth = new Date().getMonth() + 1

const showForm = ref(false)
const formError = ref<string | null>(null)
const form = ref({
  date: "",
  start_time_input: "",
  end_time_input: "",
  reason: "",
})

await Promise.all([
  overtimeStore.fetchMyOvertimes(currentYear),
  overtimeStore.fetchMonthlySummary(currentYear, currentMonth),
])

const myMonthlySummary = computed(() =>
  overtimeStore.monthlySummary.find(s => s.user_id === authStore.user?.id) ?? null
)

const computedMinutes = computed(() => {
  if (!form.value.start_time_input || !form.value.end_time_input || !form.value.date) return 0
  const start = new Date(`${form.value.date}T${form.value.start_time_input}:00`)
  const end = new Date(`${form.value.date}T${form.value.end_time_input}:00`)
  let diff = end.getTime() - start.getTime()
  if (diff === 0) return 0
  // 終了時刻が開始時刻より前 = 日をまたぐ残業（夜勤）とみなし翌日として計算
  if (diff < 0) diff += 24 * 60 * 60 * 1000
  return Math.floor(diff / 60000)
})

function fmtMinutes(m: number): string {
  const h = Math.floor(m / 60)
  const min = m % 60
  return min > 0 ? `${h}時間${min}分` : `${h}時間`
}

async function submitForm() {
  formError.value = null
  if (!form.value.date) {
    formError.value = "日付を入力してください"
    return
  }
  if (!form.value.start_time_input || !form.value.end_time_input) {
    formError.value = "開始時刻と終了時刻を入力してください"
    return
  }
  if (computedMinutes.value <= 0) {
    formError.value = "終了時刻は開始時刻より後を指定してください"
    return
  }
  if (!form.value.reason.trim()) {
    formError.value = "申請理由を入力してください"
    return
  }

  const payload: OvertimeCreatePayload = {
    date: form.value.date,
    start_time: `${form.value.date}T${form.value.start_time_input}:00`,
    end_time: `${form.value.date}T${form.value.end_time_input}:00`,
    reason: form.value.reason,
  }

  try {
    await overtimeStore.createOvertime(payload)
    showForm.value = false
    form.value = { date: "", start_time_input: "", end_time_input: "", reason: "" }
    await overtimeStore.fetchMonthlySummary(currentYear, currentMonth)
  } catch {
    formError.value = overtimeStore.error
  }
}

async function cancel(id: number) {
  try {
    await overtimeStore.cancelOvertime(id)
  } catch {
    // error は store に格納済み
  }
}

const statusMap: Record<string, { label: string; color: "amber" | "green" | "red" | "gray" }> = {
  PENDING:   { label: "承認待ち",   color: "amber" },
  APPROVED:  { label: "承認済",    color: "green" },
  REJECTED:  { label: "却下",      color: "red" },
  CANCELLED: { label: "キャンセル", color: "gray" },
}

function fmtDate(s: string) {
  return new Date(s + "T00:00:00").toLocaleDateString("ja-JP", { month: "numeric", day: "numeric", weekday: "short" })
}

function fmtTime(s: string) {
  return new Date(s).toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" })
}

const { roleTheme } = useRoleTheme()
</script>

<template>
  <div :class="['min-h-screen', roleTheme.pageBg]">
    <!-- ヘッダー -->
    <header :class="[roleTheme.header, 'shadow-lg']">
      <div class="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <NuxtLink to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div class="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center shadow">
              <UIcon name="i-heroicons-clock" class="w-5 h-5 text-white" />
            </div>
            <span class="text-lg font-bold text-white">AttendEase</span>
          </NuxtLink>
          <UIcon name="i-heroicons-chevron-right" :class="['w-4 h-4', roleTheme.sub3]" />
          <span :class="['text-sm font-medium', roleTheme.sub1]">残業申請</span>
        </div>
        <div class="flex items-center gap-3">
          <span :class="['text-sm hidden sm:block', roleTheme.sub1]">{{ authStore.user?.name }} さん</span>
          <UButton variant="ghost" size="sm" icon="i-heroicons-arrow-right-on-rectangle" class="!bg-red-500 !text-white hover:!bg-red-600 transition-all duration-200 font-medium rounded-lg" @click="authStore.logout()">
            ログアウト
          </UButton>
        </div>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-6 py-10 space-y-6">
      <!-- 月次アラートバナー -->
      <div
        v-if="myMonthlySummary && myMonthlySummary.alert"
        class="bg-orange-50 border border-orange-200 rounded-2xl p-5 flex items-start gap-3"
      >
        <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 text-orange-500 mt-0.5 flex-shrink-0" />
        <div>
          <p class="font-semibold text-orange-800 text-sm">今月の残業時間が30時間を超えています</p>
          <p class="text-orange-600 text-xs mt-0.5">
            承認済み残業: {{ fmtMinutes(myMonthlySummary.total_approved_minutes) }}
          </p>
        </div>
      </div>

      <!-- 月次サマリー（アラートなし） -->
      <div v-else-if="myMonthlySummary" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <p class="text-xs text-gray-500 mb-3 font-medium uppercase tracking-wider">
          {{ myMonthlySummary.year }}年{{ myMonthlySummary.month }}月 残業実績（承認済）
        </p>
        <p class="text-2xl font-bold text-gray-700">
          {{ fmtMinutes(myMonthlySummary.total_approved_minutes) }}
          <span class="text-sm font-normal text-gray-400 ml-1">/ 上限30時間</span>
        </p>
      </div>

      <!-- 申請ボタン / フォーム -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 class="font-semibold text-gray-800">残業申請</h2>
          <UButton
            :color="showForm ? 'gray' : 'orange'"
            :variant="showForm ? 'soft' : 'solid'"
            :icon="showForm ? 'i-heroicons-x-mark' : 'i-heroicons-plus'"
            size="sm"
            @click="showForm = !showForm; formError = null"
          >
            {{ showForm ? '閉じる' : '新規申請' }}
          </UButton>
        </div>

        <div v-if="showForm" class="px-6 py-5 border-b border-gray-100 bg-gray-50 space-y-4">
          <div v-if="formError" class="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
            {{ formError }}
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="sm:col-span-2">
              <label class="block text-xs font-medium text-gray-600 mb-1">残業日</label>
              <UInput v-model="form.date" type="date" class="w-full" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">開始時刻</label>
              <input
                v-model="form.start_time_input"
                type="time"
                class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
              >
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">終了時刻</label>
              <input
                v-model="form.end_time_input"
                type="time"
                class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
              >
            </div>
            <div class="sm:col-span-2 flex items-center gap-2">
              <UIcon name="i-heroicons-clock" class="w-4 h-4 text-gray-400" />
              <span class="text-sm text-gray-600">
                申請時間: <strong>{{ computedMinutes > 0 ? fmtMinutes(computedMinutes) : '—' }}</strong>
              </span>
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-medium text-gray-600 mb-1">申請理由</label>
              <UTextarea v-model="form.reason" placeholder="残業の理由・業務内容を入力してください" :rows="3" class="w-full" />
            </div>
          </div>

          <div class="flex justify-end gap-2">
            <UButton color="gray" variant="soft" @click="showForm = false; formError = null">キャンセル</UButton>
            <UButton color="orange" :loading="overtimeStore.isLoading" @click="submitForm">申請する</UButton>
          </div>
        </div>

        <!-- 申請一覧 -->
        <div v-if="overtimeStore.isLoading && !showForm" class="flex items-center justify-center py-16">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 text-gray-400 animate-spin" />
        </div>
        <div v-else-if="overtimeStore.myOvertimes.length === 0" class="flex flex-col items-center justify-center py-16 gap-2">
          <UIcon name="i-heroicons-clock" class="w-8 h-8 text-gray-300" />
          <p class="text-gray-400 text-sm">申請履歴がありません</p>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">日付</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">開始</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">終了</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">時間</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">理由</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">状態</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="req in overtimeStore.myOvertimes" :key="req.id" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ fmtDate(req.date) }}</td>
                <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ fmtTime(req.start_time) }}</td>
                <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ fmtTime(req.end_time) }}</td>
                <td class="px-4 py-3 font-semibold text-gray-700 whitespace-nowrap">{{ fmtMinutes(req.minutes) }}</td>
                <td class="px-4 py-3 text-gray-500 max-w-xs truncate">{{ req.reason }}</td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <div>
                    <UBadge :color="statusMap[req.status]?.color ?? 'gray'" variant="subtle" size="xs">
                      {{ statusMap[req.status]?.label ?? req.status }}
                    </UBadge>
                    <p v-if="req.reviewer_comment" class="text-xs text-gray-400 mt-1 max-w-xs truncate">{{ req.reviewer_comment }}</p>
                  </div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <UButton
                    v-if="req.status === 'PENDING'"
                    color="red"
                    variant="ghost"
                    size="xs"
                    :loading="overtimeStore.isLoading"
                    @click="cancel(req.id)"
                  >
                    キャンセル
                  </UButton>
                  <span v-else class="text-gray-300 text-xs">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>
