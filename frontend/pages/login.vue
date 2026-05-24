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
  otp, otpAttrs,
  emailHint,
  resendCooldown,
  isResending,
  credentialsErrors,
  otpErrors,
  isSubmittingCredentials,
  isSubmittingOtp,
  onSubmitCredentials,
  onSubmitOtp,
  resendOtp,
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

    <!-- ステップ2: OTP -->
    <template v-else>
      <h2 class="text-xl font-semibold text-gray-800 mb-2 text-center">認証コードを入力</h2>

      <!-- 開発用バイパス表示 -->
      <template v-if="emailHint.startsWith('[DEV]')">
        <div class="bg-yellow-50 border border-yellow-300 rounded-lg p-4 mb-4 text-center">
          <p class="text-xs font-semibold text-yellow-700 mb-1">開発モード: 認証コード</p>
          <p class="text-3xl font-mono font-bold tracking-widest text-yellow-800">
            {{ emailHint.replace('[DEV] ', '') }}
          </p>
        </div>
      </template>
      <template v-else>
        <p class="text-center text-sm text-gray-500 mb-1">
          <span class="font-medium text-gray-700">{{ emailHint }}</span> に
        </p>
        <p class="text-center text-sm text-gray-500 mb-6">6桁の認証コードを送信しました</p>
      </template>

      <UAlert
        v-if="authStore.error"
        color="red"
        variant="soft"
        icon="i-heroicons-exclamation-circle"
        :description="authStore.error"
        class="mb-5"
      />

      <form class="space-y-5" novalidate @submit.prevent="onSubmitOtp">
        <UFormGroup label="認証コード" name="otp" :error="otpErrors.otp">
          <UInput
            v-model="otp"
            v-bind="otpAttrs"
            placeholder="6桁の数字"
            size="lg"
            icon="i-heroicons-envelope"
            inputmode="numeric"
            maxlength="6"
            :disabled="isSubmittingOtp"
            autocomplete="one-time-code"
          />
          <template #hint>
            <span class="text-xs text-gray-400">有効期限: 10分</span>
          </template>
        </UFormGroup>

        <UButton
          type="submit"
          color="blue"
          block
          size="lg"
          :loading="isSubmittingOtp"
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
          :disabled="resendCooldown > 0 || isResending || isSubmittingOtp"
          :loading="isResending"
          @click="resendOtp"
        >
          {{ resendCooldown > 0 ? `再送信（${resendCooldown}秒後）` : 'コードを再送信' }}
        </UButton>

        <UButton
          type="button"
          color="gray"
          variant="ghost"
          block
          size="lg"
          :disabled="isSubmittingOtp"
          @click="backToCredentials"
        >
          戻る
        </UButton>
      </form>
    </template>
  </div>
</template>
