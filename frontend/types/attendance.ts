export type AttendanceStatus =
  | "NOT_CLOCKED_IN"
  | "PRESENT"
  | "CLOSED"
  | "CORRECTION_PENDING"
  | "CORRECTION_APPROVED"

export type WorkType = "office" | "remote"

export interface AttendanceRecord {
  id: number
  user_id: number
  date: string
  clock_in: string | null
  clock_out: string | null
  break_minutes: number
  status: AttendanceStatus
  work_type: WorkType | null
  correction_note: string | null
  work_minutes: number | null
}

export interface TodayStatusResponse {
  date: string
  status: AttendanceStatus
  record: AttendanceRecord | null
}

export interface MonthlyAttendanceResponse {
  month: string
  records: AttendanceRecord[]
  total_work_minutes: number
  total_overtime_minutes: number
}

export interface MonthlySummaryItem {
  month: string
  work_minutes: number
  overtime_minutes: number
}

export interface YearlySummaryResponse {
  year: number
  months: MonthlySummaryItem[]
  total_work_minutes: number
  total_overtime_minutes: number
}
