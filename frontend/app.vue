<script setup lang="ts">
const authStore = useAuthStore()
const notifStore = useNotificationsStore()

onMounted(() => {
  watch(
    () => authStore.isLoggedIn,
    (loggedIn) => {
      if (loggedIn) {
        notifStore.fetchUnreadCount()
        notifStore.startPolling()
      } else {
        notifStore.stopPolling()
      }
    },
    { immediate: true },
  )
})
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
  <UNotifications />
</template>
