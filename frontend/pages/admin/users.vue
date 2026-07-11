<script setup lang="ts">
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

    <main class="max-w-2xl mx-auto px-4 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <UIcon name="i-heroicons-user-plus" class="w-7 h-7 text-primary-600" />
          新規ユーザー登録
        </h1>
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
