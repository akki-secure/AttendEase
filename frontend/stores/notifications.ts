import { defineStore } from "pinia"
import type { Notification, UnreadCountResponse } from "~/types/notification"
import { extractApiError } from "~/utils/validation"

const POLL_INTERVAL_MS = 10_000

// ユーザー操作後に初期化し、バックグラウンドポーリングでも再生できるようキャッシュ
let _audioCtx: AudioContext | null = null

function getAudioContext(): AudioContext | null {
  try {
    if (!_audioCtx || _audioCtx.state === "closed") {
      _audioCtx = new AudioContext()
    }
    return _audioCtx
  } catch {
    return null
  }
}

// ログイン直後など最初のユーザー操作でAudioContextをunlock
export function unlockAudio() {
  const ctx = getAudioContext()
  if (ctx && ctx.state === "suspended") {
    ctx.resume().catch(() => {})
  }
}

async function playNotificationSound() {
  try {
    const ctx = getAudioContext()
    if (!ctx) return
    if (ctx.state === "suspended") {
      await ctx.resume()
    }

    function chime(freq: number, startAt: number, duration: number) {
      const osc = ctx!.createOscillator()
      const gain = ctx!.createGain()
      osc.connect(gain)
      gain.connect(ctx!.destination)
      osc.type = "sine"
      osc.frequency.setValueAtTime(freq, startAt)
      gain.gain.setValueAtTime(0, startAt)
      gain.gain.linearRampToValueAtTime(0.7, startAt + 0.01)
      gain.gain.exponentialRampToValueAtTime(0.001, startAt + duration)
      osc.start(startAt)
      osc.stop(startAt + duration)
    }

    const t = ctx.currentTime
    chime(1046, t, 0.45)       // ド（C6）
    chime(1318, t + 0.18, 0.5) // ミ（E6）
  } catch {
    // AudioContext not available
  }
}

export const useNotificationsStore = defineStore("notifications", () => {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()

  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  let pollTimer: ReturnType<typeof setInterval> | null = null

  function authHeaders() {
    return { Authorization: `Bearer ${authStore.token}` }
  }

  async function fetchNotifications() {
    isLoading.value = true
    error.value = null
    try {
      const data = await $fetch<Notification[]>(`${config.public.apiBase}/api/v1/notifications/me`, {
        headers: authHeaders(),
      })
      notifications.value = data
    } catch (err) {
      error.value = extractApiError(err, "通知の取得に失敗しました")
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUnreadCount() {
    try {
      const data = await $fetch<UnreadCountResponse>(`${config.public.apiBase}/api/v1/notifications/unread-count`, {
        headers: authHeaders(),
      })
      unreadCount.value = data.count
    } catch {
      // non-critical
    }
  }

  async function pollUnreadCount() {
    if (!authStore.token) return
    try {
      const data = await $fetch<UnreadCountResponse>(`${config.public.apiBase}/api/v1/notifications/unread-count`, {
        headers: authHeaders(),
      })
      if (data.count > unreadCount.value) {
        await playNotificationSound()
        if (notifications.value.length > 0 || unreadCount.value > 0) {
          await fetchNotifications()
        }
      }
      unreadCount.value = data.count
    } catch {
      // non-critical
    }
  }

  function startPolling() {
    if (pollTimer) return
    pollTimer = setInterval(pollUnreadCount, POLL_INTERVAL_MS)
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  async function markAsRead(id: number) {
    try {
      await $fetch<Notification>(`${config.public.apiBase}/api/v1/notifications/${id}/read`, {
        method: "PATCH",
        headers: authHeaders(),
      })
      const notif = notifications.value.find((n) => n.id === id)
      if (notif) {
        notif.is_read = true
        if (unreadCount.value > 0) unreadCount.value--
      }
    } catch (err) {
      error.value = extractApiError(err, "既読処理に失敗しました")
    }
  }

  async function markAllAsRead() {
    try {
      await $fetch(`${config.public.apiBase}/api/v1/notifications/read-all`, {
        method: "PATCH",
        headers: authHeaders(),
      })
      notifications.value.forEach((n) => { n.is_read = true })
      unreadCount.value = 0
    } catch (err) {
      error.value = extractApiError(err, "全既読処理に失敗しました")
    }
  }

  return {
    notifications,
    unreadCount,
    isLoading,
    error,
    fetchNotifications,
    fetchUnreadCount,
    startPolling,
    stopPolling,
    markAsRead,
    markAllAsRead,
  }
})
