# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — SQLAlchemy 2.0 Async ORM Models (PostgreSQL)

import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Enum, Integer, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SlotStatusEnum(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    HELD_PENDING_DEPOSIT = "HELD_PENDING_DEPOSIT"
    LOCKED_CONFIRMED = "LOCKED_CONFIRMED"
    COMPLETED = "COMPLETED"


class ProcedurePriorityEnum(str, enum.Enum):
    OPERATION_SURGERY = "OPERATION_SURGERY"
    GENERAL_CONSULTATION = "GENERAL_CONSULTATION"


class AppointmentSlotModel(Base):
    """PostgreSQL Schema for Clinical Appointment Slots."""

    __tablename__ = "appointment_slots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    branch_id: Mapped[str] = mapped_column(String(50), index=True)
    slot_time_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[SlotStatusEnum] = mapped_column(
        Enum(SlotStatusEnum), default=SlotStatusEnum.AVAILABLE, index=True
    )
    priority: Mapped[ProcedurePriorityEnum] = mapped_column(
        Enum(ProcedurePriorityEnum), default=ProcedurePriorityEnum.GENERAL_CONSULTATION
    )
    patient_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    checkin_code: Mapped[Optional[str]] = mapped_column(String(12), unique=True, nullable=True)
    updated_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
