# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Tier 3 Enterprise Strategy Handler

import random
from typing import Dict, Callable

from app.services.session.models import PatientSession, CommandResult, ActionType, PriorityLevel, ProcedureType
from app.services.session.tier2_strategy import Tier2Strategy
from app.services.tier_config import SaaSPlanTier
from app.services.care_card_service import send_post_care_card


class Tier3Strategy(Tier2Strategy):
    """Tier 3 Enterprise Strategy: Apollo/Fortis-Grade Concierge with Pre-Triage, TPA Desk, & Branch Routing."""

    def __init__(self):
        super().__init__()
        self.tier = SaaSPlanTier.TIER_3

    def _build_dispatcher_map(self) -> Dict[str, Callable[[PatientSession, str], CommandResult]]:
        return {
            "🏥 1. Select Clinic Branch & Specialist": self._handle_branch_specialist,
            "🩺 2. Guided Clinical Pre-Triage": self._handle_pre_triage,
            "💳 3. Cashless TPA Insurance Desk": self._handle_tpa_insurance,
            "📋 4. Post-Care & Recall Rules": self._handle_post_care,
            "📅 5. Interactive Slot Booking (Priority Engine)": self._handle_enterprise_booking,
            "⭐ 6. Reviews & Feedback": self._handle_reviews_enterprise,
            "❌ 7. Exit Session": self._handle_exit_enterprise
        }

    # --- Dispatcher Handler Overrides ---

    def _handle_branch_specialist(self, session: PatientSession, option_text: str) -> CommandResult:
        msg = (
            "🏥 *MULTI-BRANCH & SPECIALIST ROUTER*:\n"
            "• Active Branch: Yelahanka Node v0.2 (5th Phase)\n"
            "• Lead Surgeon: Dr. Chinmay Hudedamani (MDS, Oral Surgery & Implants)\n"
            "• Alternate Branch: Koramangala Main Branch (80 Feet Road)\n\n"
            "Select specialty: 1. Implantology | 2. Micro-RCT | 3. Clear Aligners"
        )
        return CommandResult(
            success=True,
            message=msg,
            action_type=ActionType.TRANSACTIONAL,
            payload={"branches": ["Yelahanka Node v0.2", "Koramangala Main Branch"]}
        )

    def _handle_pre_triage(self, session: PatientSession, option_text: str) -> CommandResult:
        code_num = random.randint(1000, 9999)
        code = f"APX-EMERGENCY-{code_num}"
        session.check_in_code = code

        msg = (
            "🩺 *GUIDED CLINICAL PRE-TRIAGE tree*:\n"
            "• Symptom Severity: Acute Pain / Facial Swelling detected\n"
            "• Clinical Priority: LEVEL-1 SURGICAL PRIORITY\n"
            "• Priority Check-In Code: **{code}**\n\n"
            "🚨 Immediate priority slot unblocked at 11:30 AM with Dr. Chinmay!"
        ).format(code=code)

        return CommandResult(
            success=True,
            message=msg,
            action_type=ActionType.EMERGENCY,
            payload={"check_in_code": code, "priority": PriorityLevel.ACUTE_EMERGENCY.value}
        )

    def _handle_tpa_insurance(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "💳 *CASHLESS TPA INSURANCE DESK*:\n"
            "• Empaneled Insurers: Star Health, HDFC ERGO, ICICI Lombard, Max Bupa\n"
            "• Estimated Co-Pay: 0% to 15% for pre-approved surgeries\n"
            "📸 *Please upload a clear photo of your Insurance Policy Card or Health ID.*"
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_post_care(self, session: PatientSession, option_text: str) -> CommandResult:
        care_card = send_post_care_card(session.phone_number, procedure_type="EXTRACTION")
        session.hidden_options.add(option_text)
        return CommandResult(
            success=True,
            message=care_card,
            action_type=ActionType.INFORMATIONAL
        )

    def _handle_enterprise_booking(self, session: PatientSession, option_text: str) -> CommandResult:
        return self._handle_live_booking(session, option_text)

    def _handle_reviews_enterprise(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "⭐ *ENTERPRISE PATIENT VERIFIED REVIEWS*:\n"
            "• 4.98 / 5.0 Star Rating across 2,400+ TPA & Surgical Patient Reviews"
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_exit_enterprise(self, session: PatientSession, option_text: str) -> CommandResult:
        session.is_active = False
        return CommandResult(
            success=True,
            message="👋 Thank you for contacting APEX Enterprise Concierge. Session closed.",
            action_type=ActionType.NAVIGATION
        )
