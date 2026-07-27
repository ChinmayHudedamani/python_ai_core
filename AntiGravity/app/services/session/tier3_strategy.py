# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Tier 3 Enterprise Strategy Handler

import secrets
import random
from typing import List, Set, Dict, Callable, Final

from app.services.session.models import PatientSession, CommandResult, ActionType, PriorityLevel
from app.services.session.base_strategy import AbstractTierStrategy
from app.services.tier_config import SaaSPlanTier
from app.services.care_card_service import CareCardService, ProcedureCategory


class Tier3Strategy(AbstractTierStrategy):
    """Tier 3 Enterprise Strategy: Apollo/Fortis-Grade Concierge with Multi-Branch, Pre-Triage, & TPA Desk."""

    MASTER_MENU: Final[List[str]] = [
        "🏥 1. Select Clinic Branch & Specialist",
        "🩺 2. Guided Clinical Pre-Triage",
        "💳 3. Cashless TPA Insurance Desk",
        "📋 4. Post-Care & Recall Rules",
        "📅 5. Interactive Slot Booking (Priority Engine)",
        "⭐ 6. Reviews & Feedback",
        "❌ 7. Exit Session",
    ]

    INFORMATIONAL_OPTIONS: Final[Set[str]] = {
        "🏥 1. Select Clinic Branch & Specialist",
        "💳 3. Cashless TPA Insurance Desk",
        "📋 4. Post-Care & Recall Rules",
        "⭐ 6. Reviews & Feedback",
    }

    def __init__(self) -> None:
        super().__init__(SaaSPlanTier.TIER_3)

    def _build_dispatcher_map(self) -> Dict[str, Callable[[PatientSession, str], CommandResult]]:
        """Polymorphic Dispatcher Map providing $O(1)$ constant-time lookup execution."""
        return {
            "🏥 1. Select Clinic Branch & Specialist": self._handle_branch_specialist,
            "🩺 2. Guided Clinical Pre-Triage": self._handle_pre_triage,
            "💳 3. Cashless TPA Insurance Desk": self._handle_tpa_desk,
            "📋 4. Post-Care & Recall Rules": self._handle_post_care,
            "📅 5. Interactive Slot Booking (Priority Engine)": self._handle_booking,
            "⭐ 6. Reviews & Feedback": self._handle_reviews,
            "❌ 7. Exit Session": self._handle_exit,
        }

    def get_menu(self, session: PatientSession) -> List[str]:
        return [item for item in self.MASTER_MENU if item not in session.hidden_options]

    def get_available_menu(self, session: PatientSession) -> List[str]:
        return self.get_menu(session)

    def process_selection(self, session: PatientSession, option_text: str) -> CommandResult:
        return self.process_option(session, option_text)

    # --- Choice Dispatch Handlers ---

    def _handle_branch_specialist(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "🏥 *APEX Network Locations & Specialists*:\n"
            "1. **Yelahanka Main Branch**: Dr. Chinmay Hudedamani (Maxillofacial Surgeon)\n"
            "2. **Koramangala Node**: Dr. Ananya Sharma (Orthodontist & Aligner Specialist)\n"
            "3. **Indiranagar Branch**: Dr. Rajesh V. (Pediatric Dentist)"
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_pre_triage(self, session: PatientSession, option_text: str) -> CommandResult:
        code_num = random.randint(1000, 9999)
        code = f"APX-EMERGENCY-{code_num}"
        session.check_in_code = code

        triage_tree = (
            "🩺 *Guided Clinical Triage*:\n"
            "Please select the severity of your symptom:\n"
            "1. 🚨 **Severe Pain / Facial Swelling / Trauma** (Auto-Issues Emergency Priority Code)\n"
            "2. 🟠 **Moderate Toothache / Sensitivity** (Priority 24-48h Slot)\n"
            "3. 🟢 **Cosmetic / Alignment Check** (Standard Evaluation Slot)\n\n"
            f"Assigned Emergency Code: **{code}**"
        )
        return CommandResult(
            success=True,
            message=triage_tree,
            action_type=ActionType.EMERGENCY,
            payload={"flow": "PRE_TRIAGE_STEP_1", "check_in_code": code}
        )

    def _handle_tpa_desk(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "💳 *Cashless TPA Insurance Desk*:\n"
            "Partner Insurers: **Star Health**, **HDFC ERGO**, **ICICI Lombard**, **Max Bupa**.\n\n"
            "📄 *Pre-Approval Steps*:\n"
            "1. Upload a clear photo of your Insurance Policy Card.\n"
            "2. Our TPA desk estimates your co-pay (Avg: 70%–100% cashless coverage).\n"
            "3. Pre-approval processed in 2–4 hours."
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_post_care(self, session: PatientSession, option_text: str) -> CommandResult:
        care_card = CareCardService.generate_care_card(ProcedureCategory.EXTRACTION, patient_name=session.phone_number)
        session.hidden_options.add(option_text)
        return CommandResult(
            success=True,
            message=care_card,
            action_type=ActionType.INFORMATIONAL
        )

    def _handle_booking(self, session: PatientSession, option_text: str) -> CommandResult:
        code = f"APX-ENT-{secrets.token_hex(2).upper()}"
        session.check_in_code = code
        msg = (
            f"📅 *Enterprise Slot Reservation Active*\n"
            f"Surgical Priority Lock Engaged.\n"
            f"Assigned Check-In Code: `{code}`"
        )
        return CommandResult(
            success=True,
            message=msg,
            action_type=ActionType.TRANSACTIONAL,
            payload={"check_in_code": code}
        )

    def _handle_reviews(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "⭐ *Enterprise Network Reviews*:\n"
            "Rated **4.95/5** across 2,000+ branch visits.\n"
            "\"TPA insurance pre-approval was completely seamless!\" — Suresh M."
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_exit(self, session: PatientSession, option_text: str) -> CommandResult:
        session.is_active = False
        return CommandResult(
            success=True,
            message="👋 Thank you for using APEX AI Enterprise Concierge.",
            action_type=ActionType.NAVIGATION
        )
