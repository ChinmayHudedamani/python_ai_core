# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Slot Model

import enum
import uuid
from datetime import date, time, datetime
from sqlalchemy import Date, Time, String, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin

class SlotStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    HELD = "HELD"
    BOOKED = "BOOKED"

class Slot(Base, TimestampMixin):
    __tablename__ = "slots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    time: Mapped[time] = mapped_column(Time, index=True, nullable=False)
    doctor_name: Mapped[str] = mapped_column(String(100), default="Dr. Chinmay Hudedamani", nullable=False)
    status: Mapped[SlotStatus] = mapped_column(SQLEnum(SlotStatus), default=SlotStatus.AVAILABLE, index=True, nullable=False)
    held_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consultation_fee: Mapped[float] = mapped_column(default=500.0)

    booking: Mapped["Booking | None"] = relationship("Booking", back_populates="slot", uselist=False)
