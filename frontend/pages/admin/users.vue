<script setup lang="ts">
import type { AdminUserListItem } from "~/types/auth"

definePageMeta({
  middleware: "admin",
})

const showPassword = ref(false)

const {
  name, nameAttrs,
  employeeId, employeeIdAttrs,
  password, passwordAttrs,
  role, roleAttrs,
  errors,
  isSubmitting,
  apiError,
  successMessage,
  onSubmit,
} = useUserCreateForm()

const roleOptions = [
  { label: "一般社員（EMPLOYEE）", value: "EMPLOYEE" },
  { label: "承認担当者（MANAGER）", value: "MANAGER" },
  { label: "システム管理者（ADMIN）", value: "ADMIN" },
]

const apiBase = useApiBase()
const authHeaders = useAuthHeaders()
const toast = useToast()

const users = ref<AdminUserListItem[]>([])
const isLoadingUsers = ref(false)
const usersError = ref<string | null>(null)
const unlockingId = ref<number | null>(null)

async function fetchUsers() {
  isLoadingUsers.value = true
  usersError.value = null
  try {
    users.value = await $fetch<AdminUserListItem[]>(
      `${apiBase}/api/v1/admin/users`,
      { headers: authHeaders() },
    )
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    usersError.value = e?.data?.detail ?? "ユーザー一覧の取得に失敗しました"
  } finally {
    isLoadingUsers.value = false
  }
}

async function unlockUser(user: AdminUserListItem) {
  unlockingId.value = user.id
  try {
    const updated = await $fetch<AdminUserListItem>(`${apiBase}/api/v1/admin/users/${user.id}/unlock`, {
      method: "PATCH", headers: authHeaders(),
    })
    const index = users.value.findIndex((u) => u.id === updated.id)
    if (index !== -1) users.value[index] = updated
    toast.add({
      title: `${user.name}（${user.employee_id}）のロックを解除しました`,
      color: "green",
      icon: "i-heroicons-check-circle",
    })
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    toast.add({ title: e?.data?.detail ?? "ロック解除に失敗しました", color: "red", icon: "i-heroicons-exclamation-circle" })
  } finally {
    unlockingId.value = null
  }
}

await fetchUsers()

watch(successMessage, (msg) => {
  if (msg) fetchUsers()
})
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

    <main class="max-w-4xl mx-auto px-4 py-10 space-y-10">
      <div>
        <div class="mb-4">
          <h1 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <UIcon name="i-heroicons-users" class="w-7 h-7 text-primary-600" />
            ユーザー一覧
          </h1>
          <p class="mt-1 text-sm text-gray-500">ロック中のアカウントはここから解除できます。</p>
        </div>

        <UAlert
          v-if="usersError"
          color="red"
          variant="soft"
          icon="i-heroicons-exclamation-circle"
          :description="usersError"
          class="mb-4"
        />

        <UCard>
          <div v-if="isLoadingUsers" class="flex items-center justify-center py-12">
            <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 text-gray-400 animate-spin" />
          </div>
          <div v-else-if="users.length === 0" class="flex flex-col items-center justify-center py-12 gap-2">
            <UIcon name="i-heroicons-users" class="w-8 h-8 text-gray-300" />
            <p class="text-gray-400 text-sm">ユーザーが登録されていません</p>
          </div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">社員ID</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">氏名</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">ロール</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">状態</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                <tr v-for="u in users" :key="u.id" class="hover:bg-gray-50 transition-colors">
                  <td class="px-4 py-3 font-mono text-gray-600 text-xs">{{ u.employee_id }}</td>
                  <td class="px-4 py-3 font-medium text-gray-700">{{ u.name }}</td>
                  <td class="px-4 py-3 text-gray-600">{{ u.role }}</td>
                  <td class="px-4 py-3">
                    <UBadge :color="u.is_locked ? 'red' : 'green'" variant="subtle" size="xs">
                      {{ u.is_locked ? 'ロック中' : '有効' }}
                    </UBadge>
                  </td>
                  <td class="px-4 py-3">
                    <UButton
                      v-if="u.is_locked"
                      color="red"
                      variant="ghost"
                      size="xs"
                      icon="i-heroicons-lock-open"
                      :loading="unlockingId === u.id"
                      :disabled="unlockingId === u.id"
                      @click="unlockUser(u)"
                    >
                      ロック解除
                    </UButton>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </UCard>
      </div>

      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <UIcon name="i-heroicons-user-plus" class="w-7 h-7 text-primary-600" />
          新規ユーザー登録
        </h2>
        <p class="mt-1 text-sm text-gray-500">社員アカウントを作成します。</p>
      </div>

      <UCard>
        <UAlert
          v-if="apiError"
          color="red"
          variant="soft"
          icon="i-heroicons-exclamation-circle"
          :description="apiError"
          class="mb-5"
        />

        <UAlert
          v-if="successMessage"
          color="green"
          variant="soft"
          icon="i-heroicons-check-circle"
          :description="successMessage"
          class="mb-5"
        />

        <form class="space-y-5" @submit.prevent="onSubmit">
          <UFormGroup label="ユーザー名" name="name" :error="errors.name" required>
            <UInput
              v-model="name"
              v-bind="nameAttrs"
              placeholder="例: 山田 太郎"
              size="lg"
              icon="i-heroicons-user"
              :disabled="isSubmitting"
            />
          </UFormGroup>

          <UFormGroup label="社員ID" name="employee_id" :error="errors.employee_id" required>
            <UInput
              v-model="employeeId"
              v-bind="employeeIdAttrs"
              placeholder="例: EMP003"
              size="lg"
              icon="i-heroicons-identification"
              :disabled="isSubmitting"
            />
          </UFormGroup>

          <UFormGroup label="パスワード" name="password" :error="errors.password" required>
            <UInput
              v-model="password"
              v-bind="passwordAttrs"
              :type="showPassword ? 'text' : 'password'"
              placeholder="パスワードを入力"
              size="lg"
              icon="i-heroicons-lock-closed"
              :disabled="isSubmitting"
              :ui="{ trailing: { padding: { lg: 'pe-10' } }, icon: { trailing: { pointer: 'pointer-events-auto' } } }"
            >
              <template #trailing>
                <UButton
                  type="button"
                  color="gray"
                  variant="link"
                  :icon="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                  :padded="false"
                  tabindex="-1"
                  @click="showPassword = !showPassword"
                />
              </template>
            </UInput>
            <template #hint>
              <span class="text-xs text-gray-400">半角英数字・大文字英語・記号のみ（8文字以上）</span>
            </template>
          </UFormGroup>

          <UFormGroup label="ロール" name="role" :error="errors.role" required>
            <USelect
              v-model="role"
              v-bind="roleAttrs"
              :options="roleOptions"
              option-attribute="label"
              value-attribute="value"
              size="lg"
              icon="i-heroicons-shield-check"
              :disabled="isSubmitting"
            />
          </UFormGroup>

          <div class="flex justify-end pt-2">
            <UButton
              type="submit"
              size="lg"
              icon="i-heroicons-user-plus"
              :loading="isSubmitting"
            >
              登録する
            </UButton>
          </div>
        </form>
      </UCard>
    </main>
  </div>
</template>
