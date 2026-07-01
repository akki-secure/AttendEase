<script setup lang="ts">
import type { CorrectionRequest } from "~/types/attendance"

definePageMeta({ middleware: ["manager-or-admin"] })

const authStore = useAuthStore()
const attendanceStore = useAttendanceStore()

await attendanceStore.fetchPendingCorrections()

const reviewTarget = ref<CorrectionRequest | null>(null)
const reviewAction = ref<"approve" | "reject">("approve")
const reviewComment = ref("")
const isModalOpen = ref(false)

function openModal(req: CorrectionRequest, action: "approve" | "reject") {
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
      await attendanceStore.approveCorrection(reviewTarget.value.id, payload)
    } else {
      await attendanceStore.rejectCorrection(reviewTarget.value.id, payload)
    }
    isModalOpen.value = false
  } catch {
    // error は store に格納済み
  }
}

function fmtDate(s: string) {
  return new Date(s + "T00:00:00").toLocaleDateString("ja-JP", { month: "numeric", day: "numeric", weekday: "short" })
}

function fmtTime(s: string | null) {
  if (!s) return "--:--"
  return new Date(s).toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" })
}

function fmtMinutes(m: number | null): string {
  if (m == null) return "--"
  const h = Math.floor(m / 60)
  const min = m % 60
  return min > 0 ? `${h}時間${min}分` : `${h}時間`
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
          <span :class="['text-sm font-medium', roleTheme.sub1]">勤怠修正承認</span>
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
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-bold text-gray-800">承認待ち一覧</h1>
        <UBadge color="amber" variant="subtle">
          {{ attendanceStore.pendingCorrections.length }}件
        </UBadge>
      </div>

      <!-- エラー -->
      <div v-if="attendanceStore.error" class="bg-red-50 border border-red-200 rounded-xl px-5 py-4 text-sm text-red-700">
        {{ attendanceStore.error }}
      </div>

      <!-- ローディング -->
      <div v-if="attendanceStore.isLoading" class="flex items-center justify-center py-20">
        <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 text-gray-400 animate-spin" />
      </div>

      <!-- 空状態 -->
      <div v-else-if="attendanceStore.pendingCorrections.length === 0" class="bg-white rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center py-20 gap-3">
        <UIcon name="i-heroicons-check-circle" class="w-12 h-12 text-green-400" />
        <p class="text-gray-500">承認待ちの修正申請はありません</p>
      </div>

      <!-- 承認待ちテーブル -->
      <div v-else class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">申請者</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">日付</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">出勤</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">退勤</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">労働時間</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">修正理由</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="req in attendanceStore.pendingCorrections" :key="req.id" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-3 font-medium text-gray-700 whitespace-nowrap">{{ req.user_name }}</td>
                <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ fmtDate(req.date) }}</td>
                <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ fmtTime(req.clock_in) }}</td>
                <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ fmtTime(req.clock_out) }}</td>
                <td class="px-4 py-3 font-semibold text-gray-700 whitespace-nowrap">{{ fmtMinutes(req.work_minutes) }}</td>
                <td class="px-4 py-3 text-gray-500 max-w-xs truncate">{{ req.correction_note }}</td>
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
              {{ reviewAction === 'approve' ? '修正申請を承認しますか？' : '修正申請を却下しますか？' }}
            </h3>
          </div>
        </template>

        <div class="space-y-4">
          <div class="bg-gray-50 rounded-lg px-4 py-3 text-sm space-y-1">
            <p><span class="text-gray-500">申請者:</span> <strong>{{ reviewTarget.user_name }}</strong></p>
            <p><span class="text-gray-500">日付:</span> {{ fmtDate(reviewTarget.date) }}</p>
            <p><span class="text-gray-500">出退勤:</span> {{ fmtTime(reviewTarget.clock_in) }} 〜 {{ fmtTime(reviewTarget.clock_out) }}（{{ fmtMinutes(reviewTarget.work_minutes) }}）</p>
            <p><span class="text-gray-500">修正理由:</span> {{ reviewTarget.correction_note }}</p>
          </div>

          <div v-if="reviewAction === 'reject'" class="bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 text-xs text-amber-700 flex items-center gap-1.5">
            <UIcon name="i-heroicons-information-circle" class="w-3.5 h-3.5" />
            却下すると修正前の出退勤時刻に戻ります
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">コメント（任意）</label>
            <UTextarea v-model="reviewComment" placeholder="コメントを入力してください" :rows="2" class="w-full" />
          </div>

          <div v-if="attendanceStore.error" class="text-sm text-red-600">{{ attendanceStore.error }}</div>
        </div>

        <template #footer>
          <div class="flex justify-end gap-2">
            <UButton color="gray" variant="soft" @click="isModalOpen = false">キャンセル</UButton>
            <UButton
              :color="reviewAction === 'approve' ? 'green' : 'red'"
              :loading="attendanceStore.isLoading"
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
