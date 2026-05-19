import { useAuthStore } from "~/stores/auth"

export default defineNuxtRouteMiddleware(() => {
  const authStore = useAuthStore()
  if (!authStore.isLoggedIn) {
    return navigateTo("/login")
  }
  if (authStore.user?.role !== "ADMIN") {
    return navigateTo("/")
  }
})
