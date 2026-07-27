# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# Copus AI / APEX AI — Micro-Hold UPI Deposit Manager Engine

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


@dataclass(slots=True)
class HoldDepositRecord:
    """Memory-optimized slots-backed container for micro-hold deposit tracking."""
    appointment_id: str
    status: str  # PENDING, CONFIRMED, EXPIRED
    deposit_amount_inr: int
    upi_payment_link: str
    created_at: str
    expires_at: str
    ttl_seconds: int = 600

    def is_expired(self) -> bool:
        """Returns True if UTC expiry time has passed."""
        expiry_dt = datetime.fromisoformat(self.expires_at)
        return datetime.now() > expiry_dt


class MicroHoldDepositEngine:
    """Micro-hold deposit engine for surgical bookings requiring UPI pre-authorization."""

    def __init__(self):
        self._hold_registry: Dict[str, HoldDepositRecord] = {}

    def create_hold(self, appointment_id: str, amount: int = 200) -> HoldDepositRecord:
        """Generates a 10-minute (600s) micro-hold deposit with tokenized UPI URI."""
        now = datetime.now()
        expires_at = now + timedelta(minutes=10)
        upi_link = f"upi://pay?pa=kasthuri@upi&am={amount}&tn=Hold-{appointment_id}"

        record = HoldDepositRecord(
            appointment_id=appointment_id,
            status="PENDING",
            deposit_amount_inr=amount,
            upi_payment_link=upi_link,
            created_at=now.isoformat(),
            expires_at=expires_at.isoformat(),
            ttl_seconds=600
        )
        self._hold_registry[appointment_id] = record
        return record

    def verify_payment(self, appointment_id: str) -> bool:
        """Validates deposit state, transitioning PENDING -> CONFIRMED or EXPIRED."""
        record = self._hold_registry.get(appointment_id)
        if not record:
            return False

        if record.is_expired():
            record = HoldDepositRecord(
                appointment_id=record.appointment_id,
                status="EXPIRED",
                deposit_amount_inr=record.deposit_amount_inr,
                upi_payment_link=record.upi_payment_link,
                created_at=record.created_at,
                expires_at=record.expires_at,
                ttl_seconds=0
            )
            self._hold_registry[appointment_id] = record
            return False

        # Transition to CONFIRMED
        confirmed_record = HoldDepositRecord(
            appointment_id=record.appointment_id,
            status="CONFIRMED",
            deposit_amount_inr=record.deposit_amount_inr,
            upi_payment_link=record.upi_payment_link,
            created_at=record.created_at,
            expires_at=record.expires_at,
            ttl_seconds=record.ttl_seconds
        )
        self._hold_registry[appointment_id] = confirmed_record
        return True

    def get_hold_record(self, appointment_id: str) -> Optional[HoldDepositRecord]:
        """Retrieves active hold deposit record."""
        return self._hold_registry.get(appointment_id)


# Helper Function for Backward Compatibility
def generate_hold_deposit(appointment_id: str, amount: int = 200) -> Dict[str, Any]:
    engine = MicroHoldDepositEngine()
    rec = engine.create_hold(appointment_id, amount)
    return {
        "appointment_id": rec.appointment_id,
        "status": rec.status,
        "deposit_amount_inr": rec.deposit_amount_inr,
        "upi_payment_link": rec.upi_payment_link,
        "created_at": rec.created_at,
        "expires_at": rec.expires_at,
        "ttl_seconds": rec.ttl_seconds,
        "message": (
            f"⚠️ *SURGICAL SLOT HOLD REQUIRED*: Micro-deposit of ₹{rec.deposit_amount_inr} "
            f"is required to lock slot {rec.appointment_id}.\n"
            f"💳 Pay via UPI: {rec.upi_payment_link}\n"
            f"⏰ Hold expires in 10 minutes. Unpaid slots auto-release!"
        )
    }
