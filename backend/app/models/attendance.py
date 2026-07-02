from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    clock_in: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    clock_out: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    break_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # PRESENT / CLOSED / CORRECTION_PENDING / CORRECTION_APPROVED
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PRESENT")
    work_type: Mapped[str | None] = mapped_column(String(10), nullable=True)  # "office" / "remote"
    correction_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_clock_in: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    original_clock_out: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    original_break_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    original_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    reviewer_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    reviewer_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="attendance_records", foreign_keys=[user_id])
