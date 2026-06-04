export function useRoleTheme() {
  const authStore = useAuthStore()

  const roleTheme = computed(() => {
    const role = authStore.user?.role
    if (role === "ADMIN") return {
      pageBg: "bg-gradient-to-br from-purple-50 via-violet-50 to-indigo-50",
      header: "bg-gradient-to-r from-purple-700 to-violet-800",
      banner: "bg-gradient-to-r from-purple-600 to-violet-700",
      sub1:   "text-purple-100",
      sub2:   "text-purple-200",
      sub3:   "text-purple-300",
      accent: "text-purple-700",
    }
    if (role === "MANAGER") return {
      pageBg: "bg-gradient-to-br from-teal-50 via-emerald-50 to-green-50",
      header: "bg-gradient-to-r from-teal-600 to-emerald-700",
      banner: "bg-gradient-to-r from-teal-500 to-emerald-600",
      sub1:   "text-teal-100",
      sub2:   "text-teal-200",
      sub3:   "text-teal-300",
      accent: "text-teal-700",
    }
    return {
      pageBg: "bg-gradient-to-br from-brand-50 via-brand-100 to-cyan-50",
      header: "bg-gradient-to-r from-brand-700 to-brand-800",
      banner: "bg-gradient-to-r from-brand-600 to-brand-700",
      sub1:   "text-brand-100",
      sub2:   "text-brand-200",
      sub3:   "text-brand-300",
      accent: "text-brand-700",
    }
  })

  return { roleTheme }
}
