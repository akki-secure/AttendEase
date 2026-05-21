<script setup lang="ts">
definePageMeta({
  layout: "auth",
  middleware: "auth",
})

const showPassword = ref(false)
const {
  step,
  employeeId, employeeIdAttrs,
  password, passwordAttrs,
  passphrase, passphraseAttrs,
  credentialsErrors,
  passphraseErrors,
  isSubmittingCredentials,
  isSubmittingPassphrase,
  onSubmitCredentials,
  onSubmitPassphrase,
  backToCredentials,
  authStore,
} = useLoginForm()
</script>

<template>
  <div>
    <!-- ステップ1: 社員ID + パスワード -->
    <template v-if="step === 'credentials'">
      <h2 class="text-xl font-semibold text-gray-800 mb-6 text-center">社員ログイン</h2>

      <UAlert
        v-if="authStore.error"
        color="red"
        variant="soft"
        icon="i-heroicons-exclamation-circle"
        :description="authStore.error"
        class="mb-5"
      />

      <form class="space-y-5" novalidate @submit.prevent="onSubmitCredentials">
        <UFormGroup label="社員ID" name="employee_id" :error="credentialsErrors.employee_id">
          <UInput
            v-model="employeeId"
            v-bind="employeeIdAttrs"
            placeholder="例: EMP001"
            size="lg"
            icon="i-heroicons-identification"
            :disabled="isSubmittingCredentials"
            autocomplete="username"
          />
        </UFormGroup>

        <UFormGroup label="パスワード" name="password" :error="credentialsErrors.password">
          <UInput
            v-model="password"
            v-bind="passwordAttrs"
            :type="showPassword ? 'text' : 'password'"
            placeholder="パスワードを入力"
            size="lg"
            icon="i-heroicons-lock-closed"
            :disabled="isSubmittingCredentials"
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
          color="blue"
          block
          size="lg"
          :loading="isSubmittingCredentials"
          class="mt-2"
        >
          次へ進む
        </UButton>
      </form>

      <p class="text-center text-sm text-gray-500 mt-4">
        アカウントをお持ちでない方は
        <NuxtLink to="/register" class="text-blue-600 hover:underline font-medium">新規登録</NuxtLink>
      </p>
    </template>

    <!-- ステップ2: 合言葉 -->
    <template v-else>
      <h2 class="text-xl font-semibold text-gray-800 mb-2 text-center">合言葉を入力してください</h2>
      <p class="text-center text-sm text-gray-500 mb-6">本人確認のため、合言葉を入力してください</p>

      <UAlert
        v-if="authStore.error"
        color="red"
        variant="soft"
        icon="i-heroicons-exclamation-circle"
        :description="authStore.error"
        class="mb-5"
      />

      <form class="space-y-5" novalidate @submit.prevent="onSubmitPassphrase">
        <UFormGroup label="合言葉" name="passphrase" :error="passphraseErrors.passphrase">
          <UInput
            v-model="passphrase"
            v-bind="passphraseAttrs"
            placeholder="合言葉を入力してください"
            size="lg"
            icon="i-heroicons-chat-bubble-left-ellipsis"
            :disabled="isSubmittingPassphrase"
            autocomplete="off"
          />
        </UFormGroup>

        <UButton
          type="submit"
          color="blue"
          block
          size="lg"
          :loading="isSubmittingPassphrase"
          class="mt-2"
        >
          ログイン
        </UButton>

        <UButton
          type="button"
          color="gray"
          variant="ghost"
          block
          size="lg"
          :disabled="isSubmittingPassphrase"
          @click="backToCredentials"
        >
          戻る
        </UButton>
      </form>
    </template>
  </div>
</template>
