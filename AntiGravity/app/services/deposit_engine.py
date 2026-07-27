# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# Copus AI / APEX AI — Micro-Hold Deposit Engine

from datetime import datetime, timedelta
from typing import Dict, Any


def generate_hold_deposit(appointment_id: str, amount: int = 200) -> Dict[str, Any]:
    """Generates a micro-hold deposit requirement for high-ticket surgical slots:
    - Changes appointment status to PENDING_DEPOSIT.
    - Generates simulated UPI payment link.
    - Sets a 10-minute (600s) expiry timer.
    """
    now = datetime.now()
    expires_at = now + timedelta(minutes=10)
    upi_link = f"upi://pay?pa=kasthuri@upi&am={amount}&pn=KasthuriDental&tr={appointment_id}"

    return {
        "appointment_id": appointment_id,
        "status": "PENDING_DEPOSIT",
        "deposit_amount_inr": amount,
        "upi_payment_link": upi_link,
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "ttl_seconds": 600,
        "message": (
            f"⚠️ *SURGICAL SLOT HOLD REQUIRED*: A micro-deposit of ₹{amount} is required "
            f"to lock slot {appointment_id}.\n"
            f"💳 Pay via UPI: {upi_link}\n"
            f"⏰ Hold expires in 10 minutes (at {expires_at.strftime('%H:%M:%S')}). Unpaid slots auto-release!"
        )
    }
