# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Tier 2.5 Beta Testing Strategy Handler

import secrets
from typing import List, Set, Dict, Callable, Final

from app.services.session.base_strategy import AbstractTierStrategy
from app.services.session.models import PatientSession, CommandResult, ActionType
from app.services.tier_config import SaaSPlanTier
from app.services.care_card_service import CareCardService, ProcedureCategory


class Tier25BetaStrategy(AbstractTierStrategy):
    """Tier 2.5 Strategy: Pro Base + Beta Previews of Clinical Pre-Triage & Digital Care Cards."""

    MASTER_MENU: Final[List[str]] = [
        "1. Doctor Details & Clinic Timings",
        "2. Cost Ranges & Pricing Sheet",
        "3. 📅 Book Appointment (Live Slots)",
        "4. 🩺 🧪 Guided Clinical Pre-Triage (Beta)",
        "5. 📋 🧪 Digital Care Cards (Beta)",
        "6. ⭐ Patient Reviews",
        "7. 🚨 Emergency Triage",
        "8. Exit Session",
    ]

    INFORMATIONAL_OPTIONS: Final[Set[str]] = {
        "1. Doctor Details & Clinic Timings",
        "2. Cost Ranges & Pricing Sheet",
        "5. 📋 🧪 Digital Care Cards (Beta)",
        "6. ⭐ Patient Reviews",
    }

    def __init__(self) -> None:
        super().__init__(SaaSPlanTier.TIER_2_5_BETA)

    def _build_dispatcher_map(self) -> Dict[str, Callable[[PatientSession, str], CommandResult]]:
        """Polymorphic Dispatcher Map providing $O(1)$ constant-time lookup execution."""
        return {
            "1. Doctor Details & Clinic Timings": self._handle_doctor_timings,
            "2. Cost Ranges & Pricing Sheet": self._handle_pricing,
            "3. 📅 Book Appointment (Live Slots)": self._handle_booking,
            "4. 🩺 🧪 Guided Clinical Pre-Triage (Beta)": self._handle_beta_pre_triage,
            "5. 📋 🧪 Digital Care Cards (Beta)": self._handle_beta_care_cards,
            "6. ⭐ Patient Reviews": self._handle_reviews,
            "7. 🚨 Emergency Triage": self._handle_emergency,
            "8. Exit Session": self._handle_exit,
        }

    def get_menu(self, session: PatientSession) -> List[str]:
        return [item for item in self.MASTER_MENU if item not in session.hidden_options]

    def get_available_menu(self, session: PatientSession) -> List[str]:
        return self.get_menu(session)

    def process_selection(self, session: PatientSession, option_text: str) -> CommandResult:
        return self.process_option(session, option_text)

    # --- Dispatcher Choice Handlers ---

    def _handle_doctor_timings(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "👨‍⚕️ *Lead Surgeon*: Dr. Chinmay Hudedamani (MDS - Oral Surgery)\n"
            "📍 *Location*: Yelahanka Node v0.2, Double Road\n"
            "🕒 *Hours*: Mon–Sat: 09:00 AM – 08:30 PM | Sun: 10:00 AM – 02:00 PM"
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_pricing(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "💳 *Standard Cost Ranges*:\n"
            "• Consultation: ₹700\n"
            "• Root Canal (RCT): ₹4,500 – ₹7,500\n"
            "• Dental Implants: Starting at ₹25,000"
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_booking(self, session: PatientSession, option_text: str) -> CommandResult:
        code = f"APX-BETA-{secrets.token_hex(2).upper()}"
        session.check_in_code = code
        msg = (
            f"📅 *Beta Live Slot Booking*\n"
            f"Surgical Priority Engine Active.\n"
            f"Assigned Check-In Code: `{code}`"
        )
        return CommandResult(
            success=True,
            message=msg,
            action_type=ActionType.TRANSACTIONAL,
            payload={"check_in_code": code}
        )

    def _handle_beta_pre_triage(self, session: PatientSession, option_text: str) -> CommandResult:
        msg = (
            "🩺 *🧪 Guided Clinical Pre-Triage (Beta Testing)*:\n"
            "Select your symptom severity:\n"
            "1. 🔴 **Severe Toothache / Swelling** (High Priority Triage)\n"
            "2. 🟡 **Moderate Sensitivity / Discomfort** (Standard Slot)\n"
            "3. 🟢 **General Consultation / Cleaning**\n\n"
            "*(Note: Full Multi-Branch Routing & TPA Insurance Desk available in Tier 3 Enterprise)*"
        )
        return CommandResult(
            success=True,
            message=msg,
            action_type=ActionType.EMERGENCY,
            payload={"flow": "BETA_TRIAGE"}
        )

    def _handle_beta_care_cards(self, session: PatientSession, option_text: str) -> CommandResult:
        sample_card = CareCardService.generate_care_card(
            ProcedureCategory.EXTRACTION, "Sample Patient (Beta Preview)"
        )
        session.hidden_options.add(option_text)
        return CommandResult(
            success=True,
            message=f"📋 *🧪 Digital Care Card Sandbox Preview*:\n\n{sample_card}\n\n📌 *Note: This option is now hidden for this session.*",
            action_type=ActionType.INFORMATIONAL
        )

    def _handle_reviews(self, session: PatientSession, option_text: str) -> CommandResult:
        body = "⭐ *Verified Patient Reviews*: Rated 4.9/5 stars across 500+ reviews."
        return self._handle_informational_option(session, option_text, body)

    def _handle_emergency(self, session: PatientSession, option_text: str) -> CommandResult:
        return CommandResult(
            success=True,
            message="🚨 *Dental Emergency*: Tap below to call immediately:\n📞 tel:+919876543210",
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
