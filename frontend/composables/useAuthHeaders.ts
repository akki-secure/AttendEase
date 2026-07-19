export function useAuthHeaders() {
  const authStore = useAuthStore()
  return () => ({ Authorization: `Bearer ${authStore.token}` })
}
