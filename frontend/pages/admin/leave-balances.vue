<script setup lang="ts">
import type { LeaveBalance } from "~/types/leave"

definePageMeta({ middleware: "admin" })

const apiBase = useApiBase()
const authStore = useAuthStore()

const currentYear = ref(new Date().getFullYear())
const balances = ref<LeaveBalance[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)
const editingId = ref<number | null>(null)
const editValue = ref(0)
const saveError = ref<string | null>(null)
const saving = ref(false)

const yearOptions = computed(() =>
  [currentYear.value - 1, currentYear.value, currentYear.value + 1].map((y) => ({
    label: `${y}年`,
    value: y,
  }))
)

async function fetchBalances() {
  isLoading.value = true
  error.value = null
  try {
    balances.value = await $fetch<LeaveBalance[]>(
      `${apiBase}/api/v1/admin/leave-balances`,
      { headers: { Authorization: `Bearer ${authStore.token}` }, params: { year: currentYear.value } },
    )
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    error.value = e?.data?.detail ?? "取得に失敗しました"
  } finally {
    isLoading.value = false
  }
}

await fetchBalances()
watch(currentYear, fetchBalances)

function startEdit(b: LeaveBalance) {
  editingId.value = b.user_id
  editValue.value = b.granted_days
  saveError.value = null
}

function cancelEdit() {
  editingId.value = null
  saveError.value = null
}

async function saveEdit(b: LeaveBalance) {
  saving.value = true
  saveError.value = null
  try {
    await $fetch(
      `${apiBase}/api/v1/admin/leave-balances/${b.user_id}/${currentYear.value}`,
      {
        method: "PUT",
        headers: { Authorization: `Bearer ${authStore.token}` },
        body: { granted_days: editValue.value },
      },
    )
    editingId.value = null
    await fetchBalances()
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    saveError.value = e?.data?.detail ?? "保存に失敗しました"
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <UIcon name="i-heroicons-clock" class="w-7 h-7 text-primary-600" />
        <span class="text-lg font-bold text-gray-800">AttendEase</span>
        <UBadge color="orange" variant="soft" class="ml-1">管理者</UBadge>
      </div>
      <UButton color="gray" variant="ghost" icon="i-heroicons-arrow-left" to="/">
        ダッシュボードへ戻る
      </UButton>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-10">
      <div class="mb-8 flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <UIcon name="i-heroicons-calendar-days" class="w-7 h-7 text-primary-600" />
            有給残日数管理
          </h1>
          <p class="mt-1 text-sm text-gray-500">社員ごとの有給付与日数を設定します。</p>
        </div>
        <USelect
          v-model="currentYear"
          :options="yearOptions"
          option-attribute="label"
          value-attribute="value"
          class="w-32"
        />
      </div>

      <UAlert
        v-if="error"
        color="red"
        variant="soft"
        icon="i-heroicons-exclamation-circle"
        :description="error"
        class="mb-5"
      />

      <UAlert
        v-if="saveError"
        color="red"
        variant="soft"
        icon="i-heroicons-exclamation-circle"
        :description="saveError"
        class="mb-5"
      />

      <UCard>
        <div v-if="isLoading" class="flex items-center justify-center py-12">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 text-gray-400 animate-spin" />
        </div>
        <div v-else-if="balances.length === 0" class="flex flex-col items-center justify-center py-12 gap-2">
          <UIcon name="i-heroicons-users" class="w-8 h-8 text-gray-300" />
          <p class="text-gray-400 text-sm">社員が登録されていません</p>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">社員名</th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">付与日数</th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">消費日数</th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">残日数</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="b in balances" :key="b.user_id" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-3 font-medium text-gray-700">{{ b.user_name }}</td>
                <td class="px-4 py-3 text-right">
                  <div v-if="editingId === b.user_id" class="flex items-center justify-end gap-2">
                    <UInput
                      v-model="editValue"
                      type="number"
                      :min="0"
                      :max="365"
                      class="w-20 text-right"
                      size="sm"
                    />
                    <span class="text-gray-400 text-xs">日</span>
                  </div>
                  <span v-else class="font-semibold text-gray-700">{{ b.granted_days }}<span class="text-xs text-gray-400 ml-1">日</span></span>
                </td>
                <td class="px-4 py-3 text-right text-orange-600 font-semibold">
                  {{ b.used_days }}<span class="text-xs text-gray-400 ml-1">日</span>
                </td>
                <td class="px-4 py-3 text-right">
                  <span class="font-bold text-lg" :class="b.remaining_days > 0 ? 'text-green-600' : 'text-red-500'">
                    {{ b.remaining_days }}
                  </span>
                  <span class="text-xs text-gray-400 ml-1">日</span>
                </td>
                <td class="px-4 py-3">
                  <div v-if="editingId === b.user_id" class="flex gap-2">
                    <UButton color="primary" size="xs" :loading="saving" @click="saveEdit(b)">保存</UButton>
                    <UButton color="gray" variant="soft" size="xs" @click="cancelEdit">キャンセル</UButton>
                  </div>
                  <UButton v-else color="gray" variant="ghost" size="xs" icon="i-heroicons-pencil" @click="startEdit(b)">
                    編集
                  </UButton>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </UCard>
    </main>
  </div>
</template>
