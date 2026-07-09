OVERTIME_ROUNDING_UNIT_MINUTES = 15


def round_down_overtime_minutes(minutes: int) -> int:
    """残業時間を15分単位で切り捨てる。"""
    return (minutes // OVERTIME_ROUNDING_UNIT_MINUTES) * OVERTIME_ROUNDING_UNIT_MINUTES


def legal_break_minutes(work_minutes: int) -> int:
    """労働基準法に基づく最低休憩時間を算出する（6時間超で45分、8時間超で60分）。"""
    if work_minutes > 8 * 60:
        return 60
    if work_minutes > 6 * 60:
        return 45
    return 0
