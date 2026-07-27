# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Code-Based Booking Model (On-Site Cash/UPI Clinic Workflow)

import enum
import uuid
from sqlalchemy import String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin

class BookingStatus(str, enum.Enum):
    SLOT_HELD = "SLOT_HELD"
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    CANCELLED = "CANCELLED"

class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False)
    slot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("slots.id", ondelete="RESTRICT"), unique=True, index=True, nullable=False)
    procedure_name: Mapped[str] = mapped_column(String(150), default="General Consultation", nullable=False)
    status: Mapped[BookingStatus] = mapped_column(SQLEnum(BookingStatus), default=BookingStatus.SLOT_HELD, index=True, nullable=False)
    
    # Check-In Confirmation Code Fields
    check_in_code: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    is_code_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="bookings")
    slot: Mapped["Slot"] = relationship("Slot", back_populates="booking")
