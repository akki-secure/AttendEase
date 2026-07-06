<script setup lang="ts">
import type { LeaveCreatePayload } from "~/types/leave"
import { LEAVE_TYPE_LABEL, LEAVE_TYPE_COLOR, isTimeBasedLeaveType } from "~/utils/leaveLabels"

const authStore = useAuthStore()
const leaveStore = useLeaveStore()

if (!authStore.isLoggedIn) {
  await navigateTo("/login")
}

const currentYear = new Date().getFullYear()

const showForm = ref(false)
const formError = ref<string | null>(null)
const form = ref<LeaveCreatePayload>({
  leave_type: "ANNUAL",
  start_date: "",
  end_date: "",
  scheduled_time: null,
  reason: "",
})

const leaveTypeOptions = [
  { label: "有給休暇", value: "ANNUAL" },
  { label: "特別休暇", value: "SPECIAL" },
  { label: "遅刻", value: "LATE" },
  { label: "早退", value: "EARLY_LEAVE" },
]

const isTimeBasedForm = computed(() => isTimeBasedLeaveType(form.value.leave_type))

const computedDays = computed(() => {
  if (!form.value.start_date || !form.value.end_date) return 0
  const diff = new Date(form.value.end_date).getTime() - new Date(form.value.start_date).getTime()
  if (diff < 0) return 0
  return Math.floor(diff / 86400000) + 1
})

const balance = computed(() => leaveStore.myBalance)

await Promise.all([
  leaveStore.fetchMyLeaves(currentYear),
  leaveStore.fetchMyBalance(currentYear),
])

async function submitForm() {
  formError.value = null
  if (!form.value.start_date || (!isTimeBasedForm.value && !form.value.end_date)) {
    formError.value = "開始日と終了日を入力してください"
    return
  }
  if (isTimeBasedForm.value) {
    form.value.end_date = form.value.start_date
    if (!form.value.scheduled_time) {
      formError.value = "本来の予定時刻を入力してください"
      return
    }
  } else {
    form.value.scheduled_time = null
    if (form.value.start_date > form.value.end_date) {
      formError.value = "終了日は開始日以降を指定してください"
      return
    }
  }
  if (!form.value.reason.trim()) {
    formError.value = "申請理由を入力してください"
    return
  }
  try {
    await leaveStore.createLeave(form.value)
    showForm.value = false
    form.value = { leave_type: "ANNUAL", start_date: "", end_date: "", scheduled_time: null, reason: "" }
    await leaveStore.fetchMyBalance(currentYear)
  } catch {
    formError.value = leaveStore.error
  }
}

async function cancel(id: number) {
  try {
    await leaveStore.cancelLeave(id)
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
          <span :class="['text-sm font-medium', roleTheme.sub1]">休暇申請</span>
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
      <!-- 有給残日数バナー -->
      <div v-if="balance" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <p class="text-xs text-gray-500 mb-3 font-medium uppercase tracking-wider">{{ currentYear }}年 有給残日数</p>
        <div class="flex items-end gap-6 flex-wrap">
          <div class="text-center">
            <p class="text-xs text-gray-400 mb-1">付与</p>
            <p class="text-2xl font-bold text-gray-700">{{ balance.granted_days }}<span class="text-sm font-normal text-gray-400 ml-1">日</span></p>
          </div>
          <div class="text-center">
            <p class="text-xs text-gray-400 mb-1">消費</p>
            <p class="text-2xl font-bold text-orange-500">{{ balance.used_days }}<span class="text-sm font-normal text-gray-400 ml-1">日</span></p>
          </div>
          <div class="text-center">
            <p class="text-xs text-gray-400 mb-1">残り</p>
            <p class="text-3xl font-bold" :class="balance.remaining_days > 0 ? 'text-green-600' : 'text-red-500'">
              {{ balance.remaining_days }}<span class="text-sm font-normal text-gray-400 ml-1">日</span>
            </p>
          </div>
        </div>
      </div>

      <!-- 申請ボタン / フォーム -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 class="font-semibold text-gray-800">休暇申請</h2>
          <UButton
            :color="showForm ? 'gray' : 'green'"
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
              <label class="block text-xs font-medium text-gray-600 mb-1">休暇種別</label>
              <USelect
                v-model="form.leave_type"
                :options="leaveTypeOptions"
                option-attribute="label"
                value-attribute="value"
                class="w-full"
              />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">{{ isTimeBasedForm ? '対象日' : '開始日' }}</label>
              <UInput v-model="form.start_date" type="date" class="w-full" />
            </div>
            <div v-if="!isTimeBasedForm">
              <label class="block text-xs font-medium text-gray-600 mb-1">終了日</label>
              <UInput v-model="form.end_date" type="date" class="w-full" />
            </div>
            <div v-if="isTimeBasedForm">
              <label class="block text-xs font-medium text-gray-600 mb-1">本来の予定時刻</label>
              <UInput :model-value="form.scheduled_time ?? undefined" @update:model-value="form.scheduled_time = $event" type="time" class="w-full" />
            </div>
            <div v-if="!isTimeBasedForm" class="sm:col-span-2 flex items-center gap-2">
              <UIcon name="i-heroicons-calendar-days" class="w-4 h-4 text-gray-400" />
              <span class="text-sm text-gray-600">申請日数: <strong>{{ computedDays }}</strong> 日</span>
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-medium text-gray-600 mb-1">申請理由</label>
              <UTextarea v-model="form.reason" placeholder="申請理由を入力してください" :rows="3" class="w-full" />
            </div>
          </div>

          <div class="flex justify-end gap-2">
            <UButton color="gray" variant="soft" @click="showForm = false; formError = null">キャンセル</UButton>
            <UButton color="green" :loading="leaveStore.isLoading" @click="submitForm">申請する</UButton>
          </div>
        </div>

        <!-- 申請一覧 -->
        <div v-if="leaveStore.isLoading && !showForm" class="flex items-center justify-center py-16">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 text-gray-400 animate-spin" />
        </div>
        <div v-else-if="leaveStore.myLeaves.length === 0" class="flex flex-col items-center justify-center py-16 gap-2">
          <UIcon name="i-heroicons-calendar" class="w-8 h-8 text-gray-300" />
          <p class="text-gray-400 text-sm">申請履歴がありません</p>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">種別</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">開始日</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">終了日</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">日数</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">理由</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">状態</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="req in leaveStore.myLeaves" :key="req.id" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-3 whitespace-nowrap">
                  <UBadge :color="LEAVE_TYPE_COLOR[req.leave_type] ?? 'gray'" variant="subtle" size="xs">
                    {{ LEAVE_TYPE_LABEL[req.leave_type] ?? req.leave_type }}
                  </UBadge>
                </td>
                <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ fmtDate(req.start_date) }}</td>
                <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ fmtDate(req.end_date) }}</td>
                <td class="px-4 py-3 font-semibold text-gray-700 whitespace-nowrap">
                  <span v-if="req.scheduled_time">予定 {{ req.scheduled_time.slice(0, 5) }}</span>
                  <span v-else>{{ req.days }}日</span>
                </td>
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
                    :loading="leaveStore.isLoading"
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
