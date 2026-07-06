export type LeaveType = "ANNUAL" | "SPECIAL" | "LATE" | "EARLY_LEAVE"
export type LeaveStatus = "PENDING" | "APPROVED" | "REJECTED" | "CANCELLED"

export interface LeaveRequest {
  id: number
  user_id: number
  user_name: string
  leave_type: LeaveType
  start_date: string
  end_date: string
  days: number
  scheduled_time: string | null
  reason: string
  status: LeaveStatus
  reviewer_id: number | null
  reviewer_comment: string | null
  reviewed_at: string | null
  created_at: string
}

export interface LeaveBalance {
  user_id: number
  user_name: string
  year: number
  granted_days: number
  used_days: number
  remaining_days: number
}

export interface LeaveCreatePayload {
  leave_type: LeaveType
  start_date: string
  end_date: string
  scheduled_time?: string | null
  reason: string
}

export interface ReviewPayload {
  comment?: string
}
