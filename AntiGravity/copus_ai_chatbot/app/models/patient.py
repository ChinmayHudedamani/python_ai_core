# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Patient Model - DPDP Act 2023 Compliance & Phonenumbers Validation

import uuid
import phonenumbers
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin

class Patient(Base, TimestampMixin):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # DPDP Act 2023 Compliance Fields
    dpdp_consent_given: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dpdp_consent_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dpdp_consent_withdrawn: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="patient", cascade="all, delete-orphan")

    @validates("phone_number")
    def validate_phone_number(self, key: str, phone: str) -> str:
        """Validates phone numbers using official phonenumbers library (region='IN')."""
        try:
            parsed = phonenumbers.parse(phone, "IN")
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError(f"Invalid mobile number for region IN: '{phone}'")
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            raise ValueError(f"Phone validation failed for '{phone}': {e}")
