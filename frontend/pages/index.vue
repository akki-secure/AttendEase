<script setup lang="ts">
const authStore = useAuthStore()

if (!authStore.isLoggedIn) {
  await navigateTo("/login")
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <UCard class="max-w-sm w-full text-center">
      <UIcon name="i-heroicons-check-circle" class="w-12 h-12 text-green-500 mx-auto mb-3" />
      <h1 class="text-xl font-bold text-gray-800 mb-1">ログイン成功</h1>
      <p class="text-gray-500 text-sm mb-4">
        ようこそ、<span class="font-medium text-gray-700">{{ authStore.user?.name }}</span> さん
      </p>
      <div class="flex flex-col gap-2">
        <UButton
          v-if="authStore.user?.role === 'ADMIN'"
          color="primary"
          variant="soft"
          icon="i-heroicons-user-plus"
          to="/admin/users"
        >
          ユーザー管理
        </UButton>
        <UButton color="gray" variant="soft" @click="authStore.logout()">ログアウト</UButton>
      </div>
    </UCard>
  </div>
</template>
