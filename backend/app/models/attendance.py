from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    clock_in: Ma    pped[datetime | None] = mapped_column(DateTime, nullable=True)
    clock_out: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    break_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # PRESENT / CLOSED / CORRECTION_PENDING / CORRECTION_APPROVED
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PRESENT")
    correction_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="attendance_records")
