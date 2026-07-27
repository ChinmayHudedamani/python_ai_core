# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Tier 2 Pro Strategy Handler

import random
from typing import Dict, Callable, Optional

from app.services.session.models import PatientSession, CommandResult, ActionType, PriorityLevel
from app.services.session.base_strategy import AbstractTierStrategy
from app.services.tier_config import SaaSPlanTier
from app.services.deposit_engine import MicroHoldDepositEngine


class Tier2Strategy(AbstractTierStrategy):
    """Tier 2 Pro Strategy: Revenue & Schedule Guard with Live Slots, OTP, Surgical Priority & Micro-Holds."""

    def __init__(self):
        super().__init__(SaaSPlanTier.TIER_2)
        self.deposit_engine = MicroHoldDepositEngine()

    def _build_dispatcher_map(self) -> Dict[str, Callable[[PatientSession, str], CommandResult]]:
        """Polymorphic Dispatcher Map providing $O(1)$ constant-time lookup execution."""
        return {
            "1. Doctor Details": self._handle_doctor_details,
            "2. Clinic Timings & Location": self._handle_timings_location,
            "3. Cost Ranges & Pricing Sheet": self._handle_cost_ranges,
            "4. 📅 Book Appointment (Live Slots)": self._handle_booking_flow,
            "5. 🔄 Reschedule / Cancel Appointment": self._handle_reschedule,
            "6. Patient Reviews": self._handle_reviews,
            "7. 🚨 Emergency Triage": self._handle_emergency_triage,
            "8. Exit Session": self._handle_exit
        }

    # --- Dispatcher Handler Methods ---

    def _handle_doctor_details(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "👨‍⚕️ *Lead Surgeon & Specialist*: Dr. Chinmay Hudedamani (MDS, Oral & Maxillofacial Surgery)\n"
            "• 12+ Years Clinical Excellence\n"
            "• Specialized in Microscopic RCT & Permanent Dental Implants"
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_timings_location(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "📍 *LOCATION & TIMINGS*:\n"
            "• Address: 5th Phase, Yelahanka New Town, Bengaluru (near Major Sandeep Unnikrishnan Road)\n"
            "• Operating Hours: Mon-Sat 09:00 AM - 08:30 PM | Sun 10:00 AM - 02:00 PM\n"
            "🚗 Free Basement Valet Parking Available!"
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_cost_ranges(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "💰 *ESTIMATED COST RANGES*:\n"
            "• General Consultation: ₹700\n"
            "• Microscopic Root Canal (RCT): ₹4,500 – ₹7,500\n"
            "• Dental Implants: ₹25,000 – ₹45,000"
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_reviews(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "⭐ *PATIENT REVIEWS & RATINGS*:\n"
            "• Google Rating: 4.9 / 5.0 (1,200+ Verified Patient Reviews)\n"
            "• 'Dr. Chinmay is incredibly gentle and painless!' — Ananya R."
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_booking_flow(self, session: PatientSession, option_text: str) -> CommandResult:
        """Triggers live slot choices and requires OTP verification."""
        if not session.is_authenticated:
            otp = f"{random.randint(1000, 9999)}"
            session.otp_code = otp
            return CommandResult(
                success=True,
                message=f"🔐 *MOBILE VERIFICATION REQUIRED*: Verification code **{otp}** sent to {session.phone_number}. Enter OTP to unlock live slots!",
                action_type=ActionType.TRANSACTIONAL,
                payload={"otp": otp, "step": "OTP_SENT", "requires_otp": True}
            )

        # Slot conflict resolution with Surgical Priority
        return self.resolve_slot_conflict(
            appointment_id=f"APX-{random.randint(1000, 9999)}",
            requesting_priority=PriorityLevel.GENERAL_CONSULTATION,
            session=session
        )

    def resolve_slot_conflict(
        self,
        appointment_id: str,
        requesting_priority: PriorityLevel = PriorityLevel.GENERAL_CONSULTATION,
        session: Optional[PatientSession] = None
    ) -> CommandResult:
        """Executes Surgical Priority Resolution:
        - OPERATION_SURGERY / SURGICAL_PRIORITY supersedes GENERAL_CONSULTATION.
        - Generates 6-character check-in code (APX-XXXX) and 10-min UPI micro-hold deposit.
        """
        code = appointment_id if appointment_id.startswith("APX-") else f"APX-{random.randint(1000, 9999)}"
        if session:
            session.check_in_code = code

        hold_record = self.deposit_engine.create_hold(code, amount=200)

        if requesting_priority == PriorityLevel.SURGICAL_PRIORITY:
            msg = (
                f"🚨 *SURGICAL PRIORITY SLOT LOCKED*:\n"
                f"• Check-In Code: **{code}**\n"
                f"• Clinical Priority: SURGICAL PRIORITY (Supersedes General Consult)\n"
                f"• Micro-Deposit Required: ₹{hold_record.amount_inr}\n"
                f"💳 UPI Link: {hold_record.upi_uri}\n"
                f"⏰ Expires in 10 minutes (at {hold_record.expires_at_iso[:19]})."
            )
        else:
            msg = (
                f"✅ *LIVE CONSULTATION SLOT LOCKED*:\n"
                f"• Doctor: Dr. Chinmay Hudedamani\n"
                f"• Slot: Tomorrow at 10:30 AM\n"
                f"• Check-In Code: **{code}**\n\n"
                f"⚠️ *SLOT HOLD REQUIRED*: Micro-deposit of ₹{hold_record.amount_inr} "
                f"is required to confirm.\n"
                f"💳 Pay via UPI: {hold_record.upi_uri}\n"
                f"⏰ Hold expires in 10 minutes."
            )

        return CommandResult(
            success=True,
            message=msg,
            action_type=ActionType.TRANSACTIONAL,
            payload={
                "check_in_code": code,
                "priority": requesting_priority.value,
                "hold_record": hold_record
            }
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
            "🚨 *24/7 EMERGENCY TRIAGE*\n"
            "If you are experiencing acute pain or bleeding, our Surgical Priority Engine has unblocked an immediate emergency slot.\n"
            "Call +919876543210 to confirm immediate arrival!"
        )
        return CommandResult(
            success=True,
            message=msg,
            action_type=ActionType.EMERGENCY,
            payload={"priority": PriorityLevel.ACUTE_EMERGENCY.value}
        )

    def _handle_exit(self, session: PatientSession, option_text: str) -> CommandResult:
        session.is_active = False
        return CommandResult(
            success=True,
            message="👋 Thank you for contacting APEX Dental. Session closed.",
            action_type=ActionType.NAVIGATION
        )
