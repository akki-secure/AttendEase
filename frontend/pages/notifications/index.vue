<script setup lang="ts">
const authStore = useAuthStore()
const notifStore = useNotificationsStore()

if (!authStore.isLoggedIn) {
  await navigateTo("/login")
}

await notifStore.fetchNotifications()

const TYPE_ICON: Record<string, string> = {
  LEAVE_REQUEST: "i-heroicons-calendar",
  LEAVE_APPROVED: "i-heroicons-check-circle",
  LEAVE_REJECTED: "i-heroicons-x-circle",
  OVERTIME_REQUEST: "i-heroicons-clock",
  OVERTIME_APPROVED: "i-heroicons-check-circle",
  OVERTIME_REJECTED: "i-heroicons-x-circle",
  OVERTIME_ALERT: "i-heroicons-exclamation-triangle",
  CORRECTION_REQUEST: "i-heroicons-pencil-square",
  CORRECTION_APPROVED: "i-heroicons-check-circle",
  CORRECTION_REJECTED: "i-heroicons-x-circle",
}

const TYPE_COLOR: Record<string, string> = {
  LEAVE_REQUEST: "text-brand-500",
  LEAVE_APPROVED: "text-green-500",
  LEAVE_REJECTED: "text-red-500",
  OVERTIME_REQUEST: "text-orange-500",
  OVERTIME_APPROVED: "text-green-500",
  OVERTIME_REJECTED: "text-red-500",
  OVERTIME_ALERT: "text-amber-500",
  CORRECTION_REQUEST: "text-orange-500",
  CORRECTION_APPROVED: "text-green-500",
  CORRECTION_REJECTED: "text-red-500",
}

function fmtDate(iso: string) {
  return new Date(iso).toLocaleString("ja-JP", {
    month: "numeric", day: "numeric", hour: "2-digit", minute: "2-digit",
  })
}

async function handleRead(id: number) {
  await notifStore.markAsRead(id)
}

async function handleReadAll() {
  await notifStore.markAllAsRead()
}

const { roleTheme } = useRoleTheme()
</script>

<template>
  <div :class="['min-h-screen', roleTheme.pageBg]">
    <!-- ヘッダー -->
    <header :class="[roleTheme.header, 'shadow-lg']">
      <div class="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
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

    <main class="max-w-3xl mx-auto px-6 py-10">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-2">
          <UIcon name="i-heroicons-bell" class="w-6 h-6 text-brand-600" />
          <h1 class="text-xl font-bold text-gray-800">通知</h1>
          <UBadge v-if="notifStore.unreadCount > 0" color="red" size="sm">
            {{ notifStore.unreadCount }}
          </UBadge>
        </div>
        <UButton
          v-if="notifStore.notifications.some(n => !n.is_read)"
          size="sm" color="gray" variant="soft"
          icon="i-heroicons-check"
          :loading="notifStore.isLoading"
          @click="handleReadAll"
        >すべて既読</UButton>
      </div>

      <!-- 通知リスト -->
      <div v-if="notifStore.isLoading" class="flex items-center justify-center h-40">
        <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 text-gray-300 animate-spin" />
      </div>

      <div v-else-if="notifStore.notifications.length === 0" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
        <UIcon name="i-heroicons-bell-slash" class="w-12 h-12 text-gray-200 mx-auto mb-3" />
        <p class="text-gray-400">通知はありません</p>
      </div>

      <div v-else class="space-y-2">
        <div
          v-for="notif in notifStore.notifications"
          :key="notif.id"
          class="bg-white rounded-xl shadow-sm border border-gray-100 px-5 py-4 flex items-start gap-4 transition-all"
          :class="notif.is_read ? 'opacity-60' : 'border-l-4 border-l-brand-400'"
        >
          <div class="flex-shrink-0 mt-0.5">
            <UIcon
              :name="TYPE_ICON[notif.type] ?? 'i-heroicons-information-circle'"
              class="w-5 h-5"
              :class="TYPE_COLOR[notif.type] ?? 'text-gray-400'"
            />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm text-gray-800 leading-snug">{{ notif.message }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ fmtDate(notif.created_at) }}</p>
          </div>
          <div v-if="!notif.is_read" class="flex-shrink-0">
            <UButton
              size="xs" color="gray" variant="ghost"
              icon="i-heroicons-check"
              @click="handleRead(notif.id)"
            >既読</UButton>
          </div>
          <div v-else class="flex-shrink-0">
            <span class="text-[10px] text-gray-300">既読</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
