<script setup lang="ts">
import { unlockAudio } from "~/stores/notifications"

const authStore = useAuthStore()
const notifStore = useNotificationsStore()

onMounted(() => {
  const onFirstInteraction = () => {
    unlockAudio()
    document.removeEventListener("pointerdown", onFirstInteraction)
  }
  document.addEventListener("pointerdown", onFirstInteraction)

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
