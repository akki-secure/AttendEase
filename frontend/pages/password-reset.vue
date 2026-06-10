<script setup lang="ts">
definePageMeta({
  layout: "auth",
  middleware: "auth",
})

const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const {
  step,
  employeeId, employeeIdAttrs,
  token, tokenAttrs,
  newPassword, newPasswordAttrs,
  confirmPassword, confirmPasswordAttrs,
  emailHint,
  apiError,
  resendCooldown,
  isResending,
  requestErrors,
  confirmErrors,
  isSubmittingRequest,
  isSubmittingConfirm,
  onSubmitRequest,
  onSubmitConfirm,
  resendToken,
  backToRequest,
} = usePasswordResetForm()

const isNoEmail = computed(() => emailHint.value === '[DEV] no-email')
const isDevCode = computed(() => !isNoEmail.value && emailHint.value.startsWith('[DEV]'))
</script>

<template>
  <div>
    <!-- ステップ1: 社員ID入力 -->
    <template v-if="step === 'request'">
      <h2 class="text-xl font-semibold text-gray-800 mb-2 text-center">パスワードをリセット</h2>
      <p class="text-sm text-gray-500 text-center mb-6">社員IDを入力すると、登録メールに認証コードを送信します</p>

      <UAlert
        v-if="apiError"
        color="red"
        variant="soft"
        icon="i-heroicons-exclamation-circle"
        :description="apiError"
        class="mb-5"
      />

      <form class="space-y-5" novalidate @submit.prevent="onSubmitRequest">
        <UFormGroup label="社員ID" name="employee_id" :error="requestErrors.employee_id">
          <UInput
            v-model="employeeId"
            v-bind="employeeIdAttrs"
            placeholder="例: EMP001"
            size="lg"
            icon="i-heroicons-identification"
            :disabled="isSubmittingRequest"
            autocomplete="username"
          />
        </UFormGroup>

        <UButton
          type="submit"
          color="blue"
          block
          size="lg"
          :loading="isSubmittingRequest"
          class="mt-2"
        >
          認証コードを送信
        </UButton>
      </form>

      <p class="text-center text-sm text-gray-500 mt-4">
        <NuxtLink to="/login" class="text-brand-600 hover:underline font-medium">ログインに戻る</NuxtLink>
      </p>
    </template>

    <!-- ステップ2: コード + 新パスワード入力 -->
    <template v-else-if="step === 'confirm'">
      <h2 class="text-xl font-semibold text-gray-800 mb-2 text-center">新しいパスワードを設定</h2>

      <!-- メール未登録 / 存在しないID（DEV モード） -->
      <div v-if="isNoEmail" class="bg-gray-50 border border-gray-300 rounded-lg p-4 mb-6 text-center">
        <p class="text-xs font-semibold text-gray-500 mb-1">開発モード</p>
        <p class="text-sm text-gray-600">このIDはメール未登録または存在しません。<br>コードは送信されていません。</p>
      </div>

      <!-- DEV: 認証コード表示 -->
      <div v-else-if="isDevCode" class="bg-yellow-50 border border-yellow-300 rounded-lg p-4 mb-4 text-center">
        <p class="text-xs font-semibold text-yellow-700 mb-1">開発モード: 認証コード</p>
        <p class="text-3xl font-mono font-bold tracking-widest text-yellow-800">
          {{ emailHint.replace('[DEV] ', '') }}
        </p>
      </div>

      <!-- 本番: メールヒント表示 -->
      <div v-else class="mb-6">
        <p class="text-center text-sm text-gray-500 mb-1">
          <span class="font-medium text-gray-700">{{ emailHint }}</span> に
        </p>
        <p class="text-center text-sm text-gray-500">6桁の認証コードを送信しました</p>
      </div>

      <!-- コード未送信の場合は入力フォームを出さずに戻るボタンのみ -->
      <UButton
        v-if="isNoEmail"
        type="button"
        color="blue"
        block
        size="lg"
        @click="backToRequest"
      >
        社員IDを入力し直す
      </UButton>

      <!-- コード送信済みの場合のみフォームを表示 -->
      <template v-else>
        <UAlert
          v-if="apiError"
          color="red"
          variant="soft"
          icon="i-heroicons-exclamation-circle"
          :description="apiError"
          class="mb-5"
        />

        <form class="space-y-5" novalidate @submit.prevent="onSubmitConfirm">
          <UFormGroup label="認証コード" name="token" :error="confirmErrors.token">
            <UInput
              v-model="token"
              v-bind="tokenAttrs"
              placeholder="6桁の数字"
              size="lg"
              icon="i-heroicons-envelope"
              inputmode="numeric"
              maxlength="6"
              :disabled="isSubmittingConfirm"
              autocomplete="one-time-code"
            />
            <template #hint>
              <span class="text-xs text-gray-400">有効期限: 10分</span>
            </template>
          </UFormGroup>

          <UFormGroup label="新しいパスワード" name="new_password" :error="confirmErrors.new_password">
            <UInput
              v-model="newPassword"
              v-bind="newPasswordAttrs"
              :type="showNewPassword ? 'text' : 'password'"
              placeholder="新しいパスワードを入力"
              size="lg"
              icon="i-heroicons-lock-closed"
              :disabled="isSubmittingConfirm"
              autocomplete="new-password"
              :ui="{ trailing: { padding: { lg: 'pe-10' } }, icon: { trailing: { pointer: 'pointer-events-auto' } } }"
            >
              <template #trailing>
                <UButton
                  type="button"
                  color="gray"
                  variant="link"
                  :icon="showNewPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                  :padded="false"
                  tabindex="-1"
                  @click="showNewPassword = !showNewPassword"
                />
              </template>
            </UInput>
            <template #hint>
              <span class="text-xs text-gray-400">半角英数字・記号のみ（8文字以上）</span>
            </template>
          </UFormGroup>

          <UFormGroup label="パスワード（確認）" name="confirm_password" :error="confirmErrors.confirm_password">
            <UInput
              v-model="confirmPassword"
              v-bind="confirmPasswordAttrs"
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder="パスワードを再入力"
              size="lg"
              icon="i-heroicons-lock-closed"
              :disabled="isSubmittingConfirm"
              autocomplete="new-password"
              :ui="{ trailing: { padding: { lg: 'pe-10' } }, icon: { trailing: { pointer: 'pointer-events-auto' } } }"
            >
              <template #trailing>
                <UButton
                  type="button"
                  color="gray"
                  variant="link"
                  :icon="showConfirmPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                  :padded="false"
                  tabindex="-1"
                  @click="showConfirmPassword = !showConfirmPassword"
                />
              </template>
            </UInput>
          </UFormGroup>

          <UButton
            type="submit"
            color="blue"
            block
            size="lg"
            :loading="isSubmittingConfirm"
            class="mt-2"
          >
            パスワードをリセット
          </UButton>

          <div class="text-center">
            <p class="text-xs text-gray-400 mb-1">コードが届かない場合</p>
            <UButton
              type="button"
              color="blue"
              variant="outline"
              block
              size="lg"
              :disabled="resendCooldown > 0 || isResending || isSubmittingConfirm"
              :loading="isResending"
              @click="resendToken"
            >
              {{ resendCooldown > 0 ? `再送信（${resendCooldown}秒後）` : 'コードを再送信する' }}
            </UButton>
          </div>

          <UButton
            type="button"
            color="gray"
            variant="ghost"
            block
            size="lg"
            :disabled="isSubmittingConfirm"
            @click="backToRequest"
          >
            戻る
          </UButton>
        </form>
      </template>
    </template>

    <!-- 完了 -->
    <template v-else>
      <div class="text-center py-4">
        <div class="flex justify-center mb-4">
          <UIcon name="i-heroicons-check-circle" class="text-green-500 text-5xl" />
        </div>
        <h2 class="text-xl font-semibold text-gray-800 mb-2">パスワードをリセットしました</h2>
        <p class="text-sm text-gray-500 mb-6">新しいパスワードでログインしてください</p>
        <UButton color="blue" block size="lg" to="/login">
          ログインへ
        </UButton>
      </div>
    </template>
  </div>
</template>
