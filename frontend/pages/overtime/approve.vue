<script setup lang="ts">
import type { OvertimeRequest } from "~/types/overtime"

definePageMeta({ middleware: ["manager-or-admin"] })

const authStore = useAuthStore()
const overtimeStore = useOvertimeStore()

const currentYear = new Date().getFullYear()
const currentMonth = new Date().getMonth() + 1

await Promise.all([
  overtimeStore.fetchPendingOvertimes(),
  overtimeStore.fetchMonthlySummary(currentYear, currentMonth),
])

const reviewTarget = ref<OvertimeRequest | null>(null)
const reviewAction = ref<"approve" | "reject">("approve")
const reviewComment = ref("")
const isModalOpen = ref(false)

function openModal(req: OvertimeRequest, action: "approve" | "reject") {
  reviewTarget.value = req
  reviewAction.value = action
  reviewComment.value = ""
  isModalOpen.value = true
}

async function confirmReview() {
  if (!reviewTarget.value) return
  const payload = { comment: reviewComment.value || undefined }
  try {
    if (reviewAction.value === "approve") {
      await overtimeStore.approveOvertime(reviewTarget.value.id, payload)
    } else {
      await overtimeStore.rejectOvertime(reviewTarget.value.id, payload)
    }
    isModalOpen.value = false
    await overtimeStore.fetchMonthlySummary(currentYear, currentMonth)
  } catch {
    // error は store に格納済み
  }
}

function fmtDate(s: string) {
  return new Date(s + "T00:00:00").toLocaleDateString("ja-JP", { month: "numeric", day: "numeric", weekday: "short" })
}

function fmtTime(s: string) {
  return new Date(s).toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" })
}

function fmtDatetime(s: string) {
  return new Date(s).toLocaleDateString("ja-JP", { month: "numeric", day: "numeric" })
}

function fmtMinutes(m: number): string {
  const h = Math.floor(m / 60)
  const min = m % 60
  return min > 0 ? `${h}時間${min}分` : `${h}時間`
}

function isAlertUser(userId: number): boolean {
  return overtimeStore.monthlySummary.find(s => s.user_id === userId)?.alert ?? false
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">
    <!-- ヘッダー -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <NuxtLink to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div class="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center shadow">
              <UIcon name="i-heroicons-clock" class="w-5 h-5 text-white" />
            </div>
            <span class="text-lg font-bold text-gray-900">AttendEase</span>
          </NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-4 h-4 text-gray-400" />
          <span class="text-sm text-gray-600 font-medium">残業承認</span>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-gray-500 hidden sm:block">{{ authStore.user?.name }} さん</span>
          <UButton color="gray" variant="soft" size="sm" icon="i-heroicons-arrow-right-on-rectangle" @click="authStore.logout()">
            ログアウト
          </UButton>
        </div>
      </div>
    </header>

    <main class="max-w-5xl mx-auto px-6 py-10 space-y-6">
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-bold text-gray-800">承認待ち一覧</h1>
        <UBadge color="amber" variant="subtle">
          {{ overtimeStore.pendingOvertimes.length }}件
        </UBadge>
      </div>

      <!-- エラー -->
      <div v-if="overtimeStore.error" class="bg-red-50 border border-red-200 rounded-xl px-5 py-4 text-sm text-red-700">
        {{ overtimeStore.error }}
      </div>

      <!-- ローディング -->
      <div v-if="overtimeStore.isLoading" class="flex items-center justify-center py-20">
        <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 text-gray-400 animate-spin" />
      </div>

      <!-- 空状態 -->
      <div v-else-if="overtimeStore.pendingOvertimes.length === 0" class="bg-white rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center py-20 gap-3">
        <UIcon name="i-heroicons-check-circle" class="w-12 h-12 text-green-400" />
        <p class="text-gray-500">承認待ちの申請はありません</p>
      </div>

      <!-- 承認待ちテーブル -->
      <div v-else class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">申請者</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">残業日</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">開始</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">終了</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">時間</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">理由</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">申請日</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr
                v-for="req in overtimeStore.pendingOvertimes"
                :key="req.id"
                :class="isAlertUser(req.user_id) ? 'bg-orange-50 hover:bg-orange-100' : 'hover:bg-gray-50'"
                class="transition-colors"
              >
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex items-center gap-1.5">
                    <span class="font-medium text-gray-700">{{ req.user_name }}</span>
                    <UIcon
                      v-if="isAlertUser(req.user_id)"
                      name="i-heroicons-exclamation-triangle"
                      class="w-3.5 h-3.5 text-orange-500"
                      title="今月の残業が30時間超"
                    />
                  </div>
                </td>
                <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ fmtDate(req.date) }}</td>
                <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ fmtTime(req.start_time) }}</td>
                <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ fmtTime(req.end_time) }}</td>
                <td class="px-4 py-3 font-semibold text-gray-700 whitespace-nowrap">{{ fmtMinutes(req.minutes) }}</td>
                <td class="px-4 py-3 text-gray-500 max-w-xs truncate">{{ req.reason }}</td>
                <td class="px-4 py-3 text-gray-400 whitespace-nowrap">{{ fmtDatetime(req.created_at) }}</td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex gap-2">
                    <UButton color="green" variant="soft" size="xs" @click="openModal(req, 'approve')">承認</UButton>
                    <UButton color="red" variant="soft" size="xs" @click="openModal(req, 'reject')">却下</UButton>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <!-- 確認モーダル -->
    <UModal v-model="isModalOpen">
      <UCard v-if="reviewTarget">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon
              :name="reviewAction === 'approve' ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'"
              :class="reviewAction === 'approve' ? 'text-green-600' : 'text-red-600'"
              class="w-5 h-5"
            />
            <h3 class="font-semibold text-gray-800">
              {{ reviewAction === 'approve' ? '申請を承認しますか？' : '申請を却下しますか？' }}
            </h3>
          </div>
        </template>

        <div class="space-y-4">
          <div class="bg-gray-50 rounded-lg px-4 py-3 text-sm space-y-1">
            <p><span class="text-gray-500">申請者:</span> <strong>{{ reviewTarget.user_name }}</strong></p>
            <p><span class="text-gray-500">残業日:</span> {{ fmtDate(reviewTarget.date) }}</p>
            <p><span class="text-gray-500">時間:</span> {{ fmtTime(reviewTarget.start_time) }} 〜 {{ fmtTime(reviewTarget.end_time) }}（{{ fmtMinutes(reviewTarget.minutes) }}）</p>
            <p><span class="text-gray-500">理由:</span> {{ reviewTarget.reason }}</p>
          </div>

          <div v-if="isAlertUser(reviewTarget.user_id)" class="bg-orange-50 border border-orange-200 rounded-lg px-3 py-2 text-xs text-orange-700 flex items-center gap-1.5">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-3.5 h-3.5" />
            この申請者は今月すでに30時間以上の残業が承認されています
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">コメント（任意）</label>
            <UTextarea v-model="reviewComment" placeholder="コメントを入力してください" :rows="2" class="w-full" />
          </div>

          <div v-if="overtimeStore.error" class="text-sm text-red-600">{{ overtimeStore.error }}</div>
        </div>

        <template #footer>
          <div class="flex justify-end gap-2">
            <UButton color="gray" variant="soft" @click="isModalOpen = false">キャンセル</UButton>
            <UButton
              :color="reviewAction === 'approve' ? 'green' : 'red'"
              :loading="overtimeStore.isLoading"
              @click="confirmReview"
            >
              {{ reviewAction === 'approve' ? '承認する' : '却下する' }}
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>
