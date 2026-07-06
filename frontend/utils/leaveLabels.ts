export const LEAVE_TYPE_LABEL: Record<string, string> = {
  ANNUAL: "有給休暇",
  SPECIAL: "特別休暇",
  LATE: "遅刻",
  EARLY_LEAVE: "早退",
}

export const LEAVE_TYPE_COLOR: Record<string, "blue" | "purple" | "orange" | "rose"> = {
  ANNUAL: "blue",
  SPECIAL: "purple",
  LATE: "orange",
  EARLY_LEAVE: "rose",
}

export function isTimeBasedLeaveType(leaveType: string): boolean {
  return leaveType === "LATE" || leaveType === "EARLY_LEAVE"
}
