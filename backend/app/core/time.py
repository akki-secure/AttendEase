OVERTIME_ROUNDING_UNIT_MINUTES = 15


def round_down_overtime_minutes(minutes: int) -> int:
    """残業時間を15分単位で切り捨てる。"""
    return (minutes // OVERTIME_ROUNDING_UNIT_MINUTES) * OVERTIME_ROUNDING_UNIT_MINUTES
