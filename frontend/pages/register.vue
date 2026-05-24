<script setup lang="ts">
definePageMeta({
  layout: "auth",
})

const config = useRuntimeConfig()
const router = useRouter()

const employeeId = ref("")
const name = ref("")
const email = ref("")
const password = ref("")
const confirmPassword = ref("")
const showPassword = ref(false)
const isSubmitting = ref(false)
const serverError = ref<string | null>(null)
const successMessage = ref<string | null>(null)

const errors = reactive({
  employee_id: "",
  name: "",
  email: "",
  password: "",
  confirmPassword: "",
})

import { ASCII_ONLY } from "~/utils/validation"

function validate() {
  errors.employee_id = employeeId.value.trim() ? "" : "社員IDを入力してください"
  errors.name = name.value.trim() ? "" : "氏名を入力してください"
  if (email.value.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
    errors.email = "正しいメールアドレスを入力してください"
  } else {
    errors.email = ""
  }
  if (!password.value) {
    errors.password = "パスワードを入力してください"
  } else if (password.value.length < 8) {
    errors.password = "パスワードは8文字以上で入力してください"
  } else if (!ASCII_ONLY.test(password.value)) {
    errors.password = "パスワードに使用できない文字が含まれています（日本語・全角文字は使用不可）"
  } else {
    errors.password = ""
  }
  errors.confirmPassword =
    confirmPassword.value === password.value ? "" : "パスワードが一致しません"
  return Object.values(errors).every((e) => !e)
}

async function onSubmit() {
  serverError.value = null
  if (!validate()) return
  isSubmitting.value = true
  try {
    await $fetch(`${config.public.apiBase}/api/v1/auth/register`, {
      method: "POST",
      body: {
        employee_id: employeeId.value,
        name: name.value,
        ...(email.value.trim() ? { email: email.value.trim() } : {}),
        password: password.value,
      },
    })
    successMessage.value = "登録が完了しました。ログインページへ移動します..."
    setTimeout(() => router.push("/login"), 1500)
  } catch (err: unknown) {
    const fetchError = err as { data?: { detail?: string } }
    serverError.value = fetchError?.data?.detail ?? "登録に失敗しました。もう一度お試しください。"
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div>
    <h2 class="text-xl font-semibold text-gray-800 mb-6 text-center">新規アカウント登録</h2>

    <UAlert
      v-if="serverError"
      color="red"
      variant="soft"
      icon="i-heroicons-exclamation-circle"
      :description="serverError"
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

    <form class="space-y-4" @submit.prevent="onSubmit">
      <UFormGroup label="社員ID" name="employee_id" :error="errors.employee_id">
        <UInput
          v-model="employeeId"
          placeholder="例: EMP001"
          size="lg"
          icon="i-heroicons-identification"
          :disabled="isSubmitting"
          autocomplete="username"
        />
      </UFormGroup>

      <UFormGroup label="氏名" name="name" :error="errors.name">
        <UInput
          v-model="name"
          placeholder="例: 山田 太郎"
          size="lg"
          icon="i-heroicons-user"
          :disabled="isSubmitting"
          autocomplete="name"
        />
      </UFormGroup>

      <UFormGroup label="メールアドレス（任意）" name="email" :error="errors.email">
        <UInput
          v-model="email"
          type="email"
          placeholder="例: yamada@example.com"
          size="lg"
          icon="i-heroicons-envelope"
          :disabled="isSubmitting"
          autocomplete="email"
        />
        <template #hint>
          <span class="text-xs text-gray-400">ログイン時のOTP認証コード送信先（後から設定可）</span>
        </template>
      </UFormGroup>

      <UFormGroup label="パスワード" name="password" :error="errors.password">
        <UInput
          v-model="password"
          :type="showPassword ? 'text' : 'password'"
          placeholder="8文字以上の半角英数字・記号"
          size="lg"
          icon="i-heroicons-lock-closed"
          :disabled="isSubmitting"
          autocomplete="new-password"
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

      <UFormGroup label="パスワード（確認）" name="confirmPassword" :error="errors.confirmPassword">
        <UInput
          v-model="confirmPassword"
          :type="showPassword ? 'text' : 'password'"
          placeholder="パスワードを再入力"
          size="lg"
          icon="i-heroicons-lock-closed"
          :disabled="isSubmitting"
          autocomplete="new-password"
        />
      </UFormGroup>

      <UButton
        type="submit"
        color="green"
        block
        size="lg"
        :loading="isSubmitting"
        class="mt-2"
      >
        登録する
      </UButton>
    </form>

    <p class="text-center text-sm text-gray-500 mt-4">
      すでにアカウントをお持ちの方は
      <NuxtLink to="/login" class="text-blue-600 hover:underline font-medium">ログイン</NuxtLink>
    </p>
  </div>
</template>
