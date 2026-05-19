<script setup lang="ts">
definePageMeta({
  layout: "auth",
  middleware: "auth",
})

const showPassword = ref(false)
const { employeeId, employeeIdAttrs, password, passwordAttrs, errors, isSubmitting, onSubmit, authStore } =
  useLoginForm()
</script>

<template>
  <div>
    <h2 class="text-xl font-semibold text-gray-800 mb-6 text-center">社員ログイン</h2>

    <UAlert
      v-if="authStore.error"
      color="red"
      variant="soft"
      icon="i-heroicons-exclamation-circle"
      :description="authStore.error"
      class="mb-5"
    />

    <form class="space-y-5" @submit.prevent="onSubmit">
      <UFormGroup label="社員ID" name="employee_id" :error="errors.employee_id">
        <UInput
          v-model="employeeId"
          v-bind="employeeIdAttrs"
          placeholder="例: EMP001"
          size="lg"
          icon="i-heroicons-identification"
          :disabled="isSubmitting"
          autocomplete="username"
        />
      </UFormGroup>

      <UFormGroup label="パスワード" name="password" :error="errors.password">
        <UInput
          v-model="password"
          v-bind="passwordAttrs"
          :type="showPassword ? 'text' : 'password'"
          placeholder="パスワードを入力"
          size="lg"
          icon="i-heroicons-lock-closed"
          :disabled="isSubmitting"
          autocomplete="current-password"
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
          <span class="text-xs text-gray-400">半角英数字・記号のみ（8文字以上）</span>
        </template>
      </UFormGroup>

      <UButton
        type="submit"
        block
        size="lg"
        :loading="isSubmitting"
        class="mt-2"
      >
        ログイン
      </UButton>
    </form>
  </div>
</template>
