# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Booking Model with Decimal Currency Integrity

import enum
import uuid
import decimal
from sqlalchemy import String, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin

class BookingStatus(str, enum.Enum):
    SLOT_HELD = "SLOT_HELD"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAID_CONFIRMED = "PAID_CONFIRMED"
    CHECKED_IN = "CHECKED_IN"

class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False)
    slot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("slots.id", ondelete="RESTRICT"), unique=True, index=True, nullable=False)
    procedure_name: Mapped[str] = mapped_column(String(150), default="General Consultation", nullable=False)
    status: Mapped[BookingStatus] = mapped_column(SQLEnum(BookingStatus), default=BookingStatus.SLOT_HELD, index=True, nullable=False)
    check_in_code: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    gateway_transaction_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    amount_paid: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), default=decimal.Decimal("500.00"), nullable=False)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="bookings")
    slot: Mapped["Slot"] = relationship("Slot", back_populates="booking")
