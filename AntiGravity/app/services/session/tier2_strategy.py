# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Tier 2 Pro Strategy Handler

import random
from typing import Dict, Callable

from app.services.session.models import PatientSession, CommandResult, ActionType, PriorityLevel
from app.services.session.tier1_strategy import Tier1Strategy
from app.services.tier_config import SaaSPlanTier
from app.services.deposit_engine import generate_hold_deposit


class Tier2Strategy(Tier1Strategy):
    """Tier 2 Pro Strategy: Revenue & Schedule Guard with Live Slots, OTP & Surgical Priority."""

    def __init__(self):
        super().__init__()
        self.tier = SaaSPlanTier.TIER_2

    def _build_dispatcher_map(self) -> Dict[str, Callable[[PatientSession, str], CommandResult]]:
        base_map = super()._build_dispatcher_map()
        base_map.update({
            "4. 📅 Book Appointment (Live Slots)": self._handle_live_booking,
            "5. 🔄 Reschedule / Cancel Appointment": self._handle_reschedule,
            "7. 🚨 Emergency Triage": self._handle_emergency_triage
        })
        return base_map

    # --- Dispatcher Handler Overrides & Extensions ---

    def _handle_live_booking(self, session: PatientSession, option_text: str) -> CommandResult:
        if not session.is_authenticated:
            # Generate OTP
            otp = f"{random.randint(1000, 9999)}"
            session.otp_code = otp
            return CommandResult(
                success=True,
                message=f"🔐 *MOBILE VERIFICATION REQUIRED*: Verification code **{otp}** sent to {session.phone_number}. Enter OTP to unlock live slots!",
                action_type=ActionType.TRANSACTIONAL,
                payload={"otp": otp, "step": "OTP_SENT"}
            )

        # Generate Check-In Code & Lock Slot
        code_num = random.randint(1000, 9999)
        check_in_code = f"APX-{code_num}"
        session.check_in_code = check_in_code

        # Check surgical micro-hold deposit trigger
        deposit_payload = generate_hold_deposit(check_in_code, amount=200)

        msg = (
            f"✅ *LIVE CONSULTATION SLOT LOCKED*:\n"
            f"• Patient Phone: {session.phone_number}\n"
            f"• Doctor: Dr. Chinmay Hudedamani\n"
            f"• Slot: Tomorrow at 10:30 AM\n"
            f"• Check-In Code: **{check_in_code}**\n\n"
            f"{deposit_payload['message']}"
        )

        return CommandResult(
            success=True,
            message=msg,
            action_type=ActionType.TRANSACTIONAL,
            payload={"check_in_code": check_in_code, "deposit": deposit_payload}
        )

    def _handle_reschedule(self, session: PatientSession, option_text: str) -> CommandResult:
        if not session.check_in_code:
            return CommandResult(
                success=False,
                message="⚠️ No active appointment found to reschedule. Please book a new slot first!",
                action_type=ActionType.TRANSACTIONAL
            )

        return CommandResult(
            success=True,
            message=f"🔄 *RESCHEDULE AGENT*: Appointment **{session.check_in_code}** can be shifted to tomorrow at 02:00 PM or 04:30 PM. Reply with desired time!",
            action_type=ActionType.TRANSACTIONAL,
            payload={"check_in_code": session.check_in_code}
        )

    def _handle_emergency_triage(self, session: PatientSession, option_text: str) -> CommandResult:
        msg = (
            "🚨 *PRIORITY EMERGENCY TRIAGE*:\n"
            "If you are experiencing acute pain or swelling, our Surgical Priority Engine has reserved an emergency slot at 11:30 AM with Dr. Chinmay.\n"
            "Call +919876543210 to confirm immediate arrival!"
        )
        return CommandResult(
            success=True,
            message=msg,
            action_type=ActionType.EMERGENCY,
            payload={"priority": PriorityLevel.SURGICAL_PRIORITY.value}
        )
