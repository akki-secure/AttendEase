from datetime import datetime, timezone

_STANDARD_WORK_MINUTES = 480  # 8 時間


def ensure_utc(dt: datetime | None) -> datetime | None:
    """Naive datetimes from SQLite are UTC – attach tzinfo so Pydantic serializes with offset."""
    if dt is None:
        return None
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def overtime_minutes(work_minutes: int) -> int:
    """残業時間を15分単位（切り捨て）で返す"""
    raw = max(work_minutes - _STANDARD_WORK_MINUTES, 0)
    return (raw // 15) * 15
