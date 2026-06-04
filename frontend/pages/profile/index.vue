<script setup lang="ts">
import { extractApiError } from "~/utils/validation"

const authStore = useAuthStore()
const config = useRuntimeConfig()
const toast = useToast()

if (!authStore.isLoggedIn) {
  await navigateTo("/login")
}

interface ProfileResponse {
  id: number
  employee_id: string
  name: string
  email: string | null
  role: string
}

const profile = ref<ProfileResponse | null>(null)
const isLoading = ref(false)
const isSaving = ref(false)

// フォーム
const name = ref("")
const email = ref("")
const currentPassword = ref("")
const newPassword = ref("")
const confirmPassword = ref("")
const showPasswordForm = ref(false)
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

async function fetchProfile() {
  isLoading.value = true
  try {
    const data = await $fetch<ProfileResponse>(`${config.public.apiBase}/api/v1/profile/me`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    profile.value = data
    name.value = data.name
    email.value = data.email ?? ""
  } catch (err) {
    toast.add({ title: extractApiError(err, "プロフィールの取得に失敗しました"), color: "red", icon: "i-heroicons-exclamation-circle" })
  } finally {
    isLoading.value = false
  }
}

await fetchProfile()

async function saveProfile() {
  if (showPasswordForm.value && newPassword.value !== confirmPassword.value) {
    toast.add({ title: "新しいパスワードが一致しません", color: "red", icon: "i-heroicons-exclamation-circle" })
    return
  }
  isSaving.value = true
  try {
    const body: Record<string, string | undefined> = {
      name: name.value || undefined,
      email: email.value || undefined,
    }
    if (showPasswordForm.value && newPassword.value) {
      body.current_password = currentPassword.value
      body.new_password = newPassword.value
    }
    const data = await $fetch<ProfileResponse>(`${config.public.apiBase}/api/v1/profile/me`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${authStore.token}` },
      body,
    })
    profile.value = data
    name.value = data.name
    email.value = data.email ?? ""
    currentPassword.value = ""
    newPassword.value = ""
    confirmPassword.value = ""
    showPasswordForm.value = false
    showCurrentPassword.value = false
    showNewPassword.value = false
    showConfirmPassword.value = false
    toast.add({ title: "プロフィールを更新しました", color: "green", icon: "i-heroicons-check-circle" })
  } catch (err) {
    toast.add({ title: extractApiError(err, "更新に失敗しました"), color: "red", icon: "i-heroicons-exclamation-circle" })
  } finally {
    isSaving.value = false
  }
}

const ROLE_LABEL: Record<string, string> = {
  EMPLOYEE: "一般社員",
  MANAGER: "マネージャー",
  ADMIN: "管理者",
}

const { roleTheme } = useRoleTheme()
</script>

<template>
  <div :class="['min-h-screen', roleTheme.pageBg]">
    <!-- ヘッダー -->
    <header :class="[roleTheme.header, 'shadow-lg']">
      <div class="max-w-2xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <NuxtLink to="/" class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center shadow">
              <UIcon name="i-heroicons-clock" class="w-5 h-5 text-white" />
            </div>
            <span class="text-lg font-bold text-white">AttendEase</span>
          </NuxtLink>
        </div>
        <div class="flex items-center gap-3">
          <NuxtLink to="/" :class="[roleTheme.sub2, 'hover:text-white text-sm transition-colors']">
            ← ダッシュボード
          </NuxtLink>
          <UButton
            variant="ghost" size="sm"
            icon="i-heroicons-arrow-right-on-rectangle"
            class="!bg-red-500 !text-white hover:!bg-red-600 transition-all duration-200 font-medium rounded-lg"
            @click="authStore.logout()"
          >ログアウト</UButton>
        </div>
      </div>
    </header>

    <main class="max-w-2xl mx-auto px-6 py-10">
      <div class="flex items-center gap-2 mb-6">
        <UIcon name="i-heroicons-user-circle" class="w-6 h-6 text-brand-600" />
        <h1 class="text-xl font-bold text-gray-800">プロフィール設定</h1>
      </div>

      <div v-if="isLoading" class="flex items-center justify-center h-40">
        <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 text-gray-300 animate-spin" />
      </div>

      <div v-else-if="profile" class="space-y-4">
        <!-- 基本情報 -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-4">
          <h2 class="text-base font-semibold text-gray-800 mb-4">基本情報</h2>

          <!-- 社員ID (読み取り専用) -->
          <div>
            <label class="block text-sm text-gray-500 mb-1">社員ID</label>
            <div class="bg-gray-50 rounded-lg px-4 py-3 text-gray-600 font-mono text-sm border border-gray-200">
              {{ profile.employee_id }}
            </div>
          </div>

          <!-- ロール (読み取り専用) -->
          <div>
            <label class="block text-sm text-gray-500 mb-1">ロール</label>
            <div class="bg-gray-50 rounded-lg px-4 py-3 text-gray-600 text-sm border border-gray-200">
              {{ ROLE_LABEL[profile.role] ?? profile.role }}
            </div>
          </div>

          <!-- 氏名 -->
          <div>
            <label class="block text-sm text-gray-500 mb-1">氏名</label>
            <input
              v-model="name"
              type="text"
              placeholder="氏名"
              class="w-full bg-white border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400"
            />
          </div>

          <!-- メールアドレス -->
          <div>
            <label class="block text-sm text-gray-500 mb-1">メールアドレス</label>
            <input
              v-model="email"
              type="email"
              placeholder="メールアドレス（通知の送信先）"
              class="w-full bg-white border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400"
            />
            <p class="text-xs text-gray-400 mt-1">申請・承認の通知メールを受け取るために使用されます</p>
          </div>
        </div>

        <!-- パスワード変更 -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-semibold text-gray-800">パスワード変更</h2>
            <UButton
              size="sm" color="gray" variant="soft"
              :icon="showPasswordForm ? 'i-heroicons-chevron-up' : 'i-heroicons-key'"
              @click="showPasswordForm = !showPasswordForm"
            >{{ showPasswordForm ? '閉じる' : '変更する' }}</UButton>
          </div>

          <div v-if="showPasswordForm" class="space-y-3">
            <div>
              <label class="block text-sm text-gray-500 mb-1">現在のパスワード</label>
              <div class="relative">
                <input
                  v-model="currentPassword"
                  :type="showCurrentPassword ? 'text' : 'password'"
                  placeholder="現在のパスワード"
                  class="w-full bg-white border border-gray-300 rounded-lg px-4 py-3 pr-11 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400"
                />
                <button
                  type="button"
                  class="absolute inset-y-0 right-3 flex items-center text-gray-400 hover:text-gray-600"
                  @click="showCurrentPassword = !showCurrentPassword"
                >
                  <UIcon :name="showCurrentPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-5 h-5" />
                </button>
              </div>
            </div>
            <div>
              <label class="block text-sm text-gray-500 mb-1">新しいパスワード</label>
              <div class="relative">
                <input
                  v-model="newPassword"
                  :type="showNewPassword ? 'text' : 'password'"
                  placeholder="8文字以上"
                  class="w-full bg-white border border-gray-300 rounded-lg px-4 py-3 pr-11 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400"
                />
                <button
                  type="button"
                  class="absolute inset-y-0 right-3 flex items-center text-gray-400 hover:text-gray-600"
                  @click="showNewPassword = !showNewPassword"
                >
                  <UIcon :name="showNewPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-5 h-5" />
                </button>
              </div>
            </div>
            <div>
              <label class="block text-sm text-gray-500 mb-1">新しいパスワード（確認）</label>
              <div class="relative">
                <input
                  v-model="confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  placeholder="もう一度入力"
                  class="w-full bg-white border border-gray-300 rounded-lg px-4 py-3 pr-11 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400"
                  :class="confirmPassword && newPassword !== confirmPassword ? 'border-red-400 focus:ring-red-400' : ''"
                />
                <button
                  type="button"
                  class="absolute inset-y-0 right-3 flex items-center text-gray-400 hover:text-gray-600"
                  @click="showConfirmPassword = !showConfirmPassword"
                >
                  <UIcon :name="showConfirmPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-5 h-5" />
                </button>
              </div>
              <p v-if="confirmPassword && newPassword !== confirmPassword" class="text-xs text-red-500 mt-1">パスワードが一致しません</p>
            </div>
          </div>
        </div>

        <!-- 保存ボタン -->
        <div class="flex justify-end">
          <UButton
            color="indigo" size="md"
            icon="i-heroicons-check"
            :loading="isSaving"
            :disabled="isSaving"
            @click="saveProfile"
          >保存する</UButton>
        </div>
      </div>
    </main>
  </div>
</template>
