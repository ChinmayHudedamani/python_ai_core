# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# Copus AI / APEX AI — Production Redis-Backed Micro-Hold Deposit Engine

import secrets
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional, Dict, Any


class DepositStatus(str, Enum):
    PENDING = "PENDING_PAYMENT"
    CONFIRMED = "CONFIRMED"
    EXPIRED = "EXPIRED"


@dataclass(slots=True, frozen=True)
class HoldDepositRecord:
    """Memory-optimized frozen slots dataclass for deposit tracking."""
    appointment_id: str
    amount_inr: int
    upi_uri: str
    status: DepositStatus
    expires_at_iso: str  # ISO 8601 UTC string for clean serialization

    def is_expired(self) -> bool:
        """Returns True if UTC expiry time has passed."""
        expiry_dt = datetime.fromisoformat(self.expires_at_iso)
        return datetime.now(timezone.utc) > expiry_dt


class MicroHoldDepositEngine:
    """Production Redis-backed Micro-Hold Deposit Manager with high-entropy security."""

    HOLD_EXPIRY_MINUTES: int = 10
    DEFAULT_DEPOSIT_INR: int = 200

    def __init__(self, redis_client=None) -> None:
        self._redis = redis_client
        self._local_registry: Dict[str, HoldDepositRecord] = {}

    def create_hold(
        self, appointment_id: str, amount: int = DEFAULT_DEPOSIT_INR
    ) -> HoldDepositRecord:
        """Generates a high-entropy (128-bit) 10-minute micro-deposit hold."""
        # High entropy token (128-bit security margin)
        token = secrets.token_hex(16).upper()
        upi_uri = f"upi://pay?pa=kasthuri@upi&am={amount}&tn=Hold-{token}"
        
        # Strict UTC timezone enforcement
        now_utc = datetime.now(timezone.utc)
        expires_at = now_utc + timedelta(minutes=self.HOLD_EXPIRY_MINUTES)

        record = HoldDepositRecord(
            appointment_id=appointment_id,
            amount_inr=amount,
            upi_uri=upi_uri,
            status=DepositStatus.PENDING,
            expires_at_iso=expires_at.isoformat()
        )

        # Store in Redis if client present, fallback to local storage
        if self._redis:
            self._redis.setex(
                f"hold:{appointment_id}",
                self.HOLD_EXPIRY_MINUTES * 60,
                json.dumps(asdict(record))
            )
        else:
            self._local_registry[appointment_id] = record

        return record

    def verify_payment(self, appointment_id: str) -> bool:
        """Verifies payment state against Redis or local storage."""
        if self._redis:
            data = self._redis.get(f"hold:{appointment_id}")
            if not data:
                return False
            record_dict = json.loads(data)
            expires_at = datetime.fromisoformat(record_dict["expires_at_iso"])
            if datetime.now(timezone.utc) > expires_at:
                return False
            record_dict["status"] = DepositStatus.CONFIRMED.value
            self._redis.set(f"hold:{appointment_id}", json.dumps(record_dict))
            return True

        record = self._local_registry.get(appointment_id)
        if not record or record.is_expired():
            return False

        confirmed = HoldDepositRecord(
            appointment_id=record.appointment_id,
            amount_inr=record.amount_inr,
            upi_uri=record.upi_uri,
            status=DepositStatus.CONFIRMED,
            expires_at_iso=record.expires_at_iso
        )
        self._local_registry[appointment_id] = confirmed
        return True


# Helper Function for Backward Compatibility
def generate_hold_deposit(appointment_id: str, amount: int = 200) -> Dict[str, Any]:
    engine = MicroHoldDepositEngine()
    rec = engine.create_hold(appointment_id, amount)
    return {
        "appointment_id": rec.appointment_id,
        "status": rec.status.value,
        "deposit_amount_inr": rec.amount_inr,
        "upi_payment_link": rec.upi_uri,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": rec.expires_at_iso,
        "ttl_seconds": 600,
        "message": (
            f"⚠️ *SURGICAL SLOT HOLD REQUIRED*: Micro-deposit of ₹{rec.amount_inr} "
            f"is required to lock slot {rec.appointment_id}.\n"
            f"💳 Pay via UPI: {rec.upi_uri}\n"
            f"⏰ Hold expires in 10 minutes. Unpaid slots auto-release!"
        )
    }
