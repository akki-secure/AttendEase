export type OvertimeStatus = "PENDING" | "APPROVED" | "REJECTED" | "CANCELLED"

export interface OvertimeRequest {
  id: number
  user_id: number
  user_name: string
  date: string
  start_time: string
  end_time: string
  minutes: number
  reason: string
  status: OvertimeStatus
  reviewer_id: number | null
  reviewer_comment: string | null
  reviewed_at: string | null
  created_at: string
}

export interface OvertimeCreatePayload {
  date: string
  start_time: string
  end_time: string
  reason: string
}

export interface OvertimeMonthlySummary {
  user_id: number
  user_name: string
  year: number
  month: number
  total_approved_minutes: number
  alert: boolean
}

export interface ReviewPayload {
  comment?: string
}
