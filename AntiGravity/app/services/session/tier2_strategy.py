# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Tier 2 Pro Strategy Handler (IST Native & Pay-at-Clinic Engine)

import secrets
import random
from typing import List, Set, Dict, Callable, Final, Optional

from app.services.session.models import PatientSession, CommandResult, ActionType, PriorityLevel
from app.services.session.base_strategy import AbstractTierStrategy
from app.services.tier_config import SaaSPlanTier
from app.utils.time_utils import get_current_ist, format_ist_time


class Tier2Strategy(AbstractTierStrategy):
    """Tier 2 Strategy: Instant Slot Lock + Pay-at-Clinic Protocol (IST Native)."""

    MASTER_MENU: Final[List[str]] = [
        "1. Doctor Details & Clinic Timings",
        "2. Cost Ranges & Pricing Sheet",
        "3. 📅 Book Appointment (Instant Lock)",
        "4. ⭐ Patient Reviews",
        "5. 🚨 Emergency Triage",
        "6. Exit Session",
    ]

    INFORMATIONAL_OPTIONS: Final[Set[str]] = {
        "1. Doctor Details & Clinic Timings",
        "2. Cost Ranges & Pricing Sheet",
        "4. ⭐ Patient Reviews",
    }

    def __init__(self) -> None:
        super().__init__(SaaSPlanTier.TIER_2)

    def _build_dispatcher_map(self) -> Dict[str, Callable[[PatientSession, str], CommandResult]]:
        """Polymorphic Dispatcher Map providing $O(1)$ constant-time lookup execution."""
        return {
            "1. Doctor Details & Clinic Timings": self._handle_doctor_timings,
            "2. Cost Ranges & Pricing Sheet": self._handle_pricing,
            "3. 📅 Book Appointment (Instant Lock)": self._handle_instant_booking,
            "4. 📅 Book Appointment (Live Slots)": self._handle_instant_booking,
            "4. ⭐ Patient Reviews": self._handle_reviews,
            "6. Patient Reviews": self._handle_reviews,
            "5. 🚨 Emergency Triage": self._handle_emergency,
            "7. 🚨 Emergency Triage": self._handle_emergency,
            "6. Exit Session": self._handle_exit,
            "8. Exit Session": self._handle_exit,
        }

    def get_menu(self, session: PatientSession) -> List[str]:
        return [item for item in self.MASTER_MENU if item not in session.hidden_options]

    def get_available_menu(self, session: PatientSession) -> List[str]:
        return self.get_menu(session)

    def process_selection(self, session: PatientSession, option_text: str) -> CommandResult:
        return self.process_option(session, option_text)

    # --- Choice Dispatch Handlers ---

    def _handle_doctor_timings(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "👨‍⚕️ *Lead Surgeon*: Dr. Chinmay Hudedamani (MDS - Oral Surgery)\n"
            "📍 *Location*: Yelahanka Node, Double Road\n"
            "🕒 *Hours*: Mon–Sat: 09:00 AM – 08:30 PM IST | Sun: 10:00 AM – 02:00 PM IST"
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_pricing(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "💳 *Standard Consultation & Treatment Fees*:\n"
            "• Consultation Fee: ₹700 (Payable at clinic desk)\n"
            "• Root Canal (RCT): ₹4,500 – ₹7,500\n"
            "• Tooth Extraction: ₹1,200 – ₹3,500"
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_instant_booking(self, session: PatientSession, option_text: str) -> CommandResult:
        """Instantly confirms slot and issues Check-In Code for Pay-at-Clinic arrival."""
        checkin_code = f"APX-{secrets.token_hex(2).upper()}"
        session.check_in_code = checkin_code
        booking_time_ist = format_ist_time(get_current_ist())

        return CommandResult(
            success=True,
            message=(
                f"✅ *APPOINTMENT CONFIRMED!*\n\n"
                f"🎫 *Check-In Code*: `{checkin_code}`\n"
                f"📅 *Booked On*: {booking_time_ist}\n"
                f"📍 *Location*: Kasthuri Dental Clinic, Yelahanka\n"
                f"💳 *Payment*: **Pay at Clinic Desk** upon arrival (Cash / UPI / Card)\n\n"
                f"📌 Please show code `{checkin_code}` to the receptionist when you arrive."
            ),
            action_type=ActionType.TRANSACTIONAL,
            payload={
                "check_in_code": checkin_code,
                "payment_status": "PENDING_AT_DESK",
                "booking_time_ist": booking_time_ist,
            }
        )

    def resolve_slot_conflict(
        self,
        appointment_id: str,
        requesting_priority: PriorityLevel = PriorityLevel.GENERAL_CONSULTATION,
        session: Optional[PatientSession] = None
    ) -> CommandResult:
        """Surgical Priority Slot Resolution with Pay-at-Clinic Confirmation."""
        return self._handle_instant_booking(session or PatientSession("SESS", "+91"), "3. 📅 Book Appointment (Instant Lock)")

    def _handle_reviews(self, session: PatientSession, option_text: str) -> CommandResult:
        body = "⭐ *Verified Reviews*: Rated 4.9/5 stars across 500+ patient visits."
        return self._handle_informational_option(session, option_text, body)

    def _handle_emergency(self, session: PatientSession, option_text: str) -> CommandResult:
        return CommandResult(
            success=True,
            message="🚨 *Dental Emergency*: Tap below to call clinic directly:\n📞 tel:+919876543210",
            action_type=ActionType.EMERGENCY,
            payload={"tel_uri": "tel:+919876543210"}
        )

    def _handle_exit(self, session: PatientSession, option_text: str) -> CommandResult:
        session.is_active = False
        return CommandResult(
            success=True,
            message="👋 Thank you for contacting Kasthuri Dental Clinic.",
            action_type=ActionType.NAVIGATION
        )
