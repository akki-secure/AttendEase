export interface Notification {
  id: number
  type: string
  message: string
  is_read: boolean
  created_at: string
}

export interface UnreadCountResponse {
  count: number
}
