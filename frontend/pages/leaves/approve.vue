<script setup lang="ts">
import type { LeaveRequest } from "~/types/leave"

definePageMeta({ middleware: ["manager-or-admin"] })

const authStore = useAuthStore()
const leaveStore = useLeaveStore()

await leaveStore.fetchPendingLeaves()

const reviewTarget = ref<LeaveRequest | null>(null)
const reviewAction = ref<"approve" | "reject">("approve")
const reviewComment = ref("")
const isModalOpen = ref(false)

function openModal(req: LeaveRequest, action: "approve" | "reject") {
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
      await leaveStore.approveLeave(reviewTarget.value.id, payload)
    } else {
      await leaveStore.rejectLeave(reviewTarget.value.id, payload)
    }
    isModalOpen.value = false
  } catch {
    // error は store に格納済み
  }
}

const leaveTypeLabel: Record<string, string> = {
  ANNUAL:  "有給休暇",
  SPECIAL: "特別休暇",
}

function fmtDate(s: string) {
  return new Date(s + "T00:00:00").toLocaleDateString("ja-JP", { month: "numeric", day: "numeric", weekday: "short" })
}

function fmtDatetime(s: string) {
  return new Date(s).toLocaleDateString("ja-JP", { month: "numeric", day: "numeric" })
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">
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
          <span class="text-sm text-blue-100 font-medium">休暇承認</span>
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
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-bold text-gray-800">承認待ち一覧</h1>
        <UBadge color="amber" variant="subtle">
          {{ leaveStore.pendingLeaves.length }}件
        </UBadge>
      </div>

      <!-- エラー -->
      <div v-if="leaveStore.error" class="bg-red-50 border border-red-200 rounded-xl px-5 py-4 text-sm text-red-700">
        {{ leaveStore.error }}
      </div>

      <!-- ローディング -->
      <div v-if="leaveStore.isLoading" class="flex items-center justify-center py-20">
        <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 text-gray-400 animate-spin" />
      </div>

      <!-- 空状態 -->
      <div v-else-if="leaveStore.pendingLeaves.length === 0" class="bg-white rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center py-20 gap-3">
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
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">種別</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">開始日</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">終了日</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">日数</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">理由</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">申請日</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="req in leaveStore.pendingLeaves" :key="req.id" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-3 font-medium text-gray-700 whitespace-nowrap">{{ req.user_name }}</td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <UBadge :color="req.leave_type === 'ANNUAL' ? 'blue' : 'purple'" variant="subtle" size="xs">
                    {{ leaveTypeLabel[req.leave_type] }}
                  </UBadge>
                </td>
                <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ fmtDate(req.start_date) }}</td>
                <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ fmtDate(req.end_date) }}</td>
                <td class="px-4 py-3 font-semibold text-gray-700 whitespace-nowrap">{{ req.days }}日</td>
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
            <p><span class="text-gray-500">種別:</span> {{ leaveTypeLabel[reviewTarget.leave_type] }}</p>
            <p><span class="text-gray-500">期間:</span> {{ fmtDate(reviewTarget.start_date) }} 〜 {{ fmtDate(reviewTarget.end_date) }}（{{ reviewTarget.days }}日）</p>
            <p><span class="text-gray-500">理由:</span> {{ reviewTarget.reason }}</p>
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">コメント（任意）</label>
            <UTextarea v-model="reviewComment" placeholder="コメントを入力してください" :rows="2" class="w-full" />
          </div>

          <div v-if="leaveStore.error" class="text-sm text-red-600">{{ leaveStore.error }}</div>
        </div>

        <template #footer>
          <div class="flex justify-end gap-2">
            <UButton color="gray" variant="soft" @click="isModalOpen = false">キャンセル</UButton>
            <UButton
              :color="reviewAction === 'approve' ? 'green' : 'red'"
              :loading="leaveStore.isLoading"
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
