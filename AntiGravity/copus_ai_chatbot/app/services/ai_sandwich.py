# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Multi-Resilient Gateway & AI Sandwich Engine

import re
from typing import List
from app.services.session.models import SaaSPlanTier, CommandResult, ActionType
from app.services.session.session_context import SessionContextManager
from app.services.nlm_engine import LocalNLMEngine, BranchAndBoundEngine


class AISandwichEngine:
    """
    Multi-Resilient Gateway Manager.
    • Tiers 1 & 2: Direct $0-cost deterministic dispatch.
    • Tier 2.5 (Beta): Primary Local NLM Engine + Branch-and-Bound Fallback.
    • Tier 3 (Enterprise): LLM Sandwich -> Local NLM Fallback -> Branch-and-Bound Fallback.
    """

    CONFIDENCE_THRESHOLD: float = 0.35

    def __init__(self, session_manager: SessionContextManager) -> None:
        self._ctx = session_manager

    def process_patient_input(self, raw_user_text: str) -> CommandResult:
        active_tier = self._ctx.session_state_obj.active_tier if hasattr(self._ctx, "session_state_obj") else self._ctx.get_strategy(SaaSPlanTier.TIER_1).tier

        # Ingress Guardrail Check
        sanitized_text = self._ingress_guardrail(raw_user_text)
        if self._is_acute_emergency(sanitized_text):
            return CommandResult(
                success=True,
                message="🚨 *ACUTE CLINICAL EMERGENCY*: Call duty surgeon immediately:\n📞 tel:+919876543210",
                action_type=ActionType.EMERGENCY,
                payload={"tel_uri": "tel:+919876543210"}
            )

        # 🟢🟡 TIERS 1 & 2: Direct Deterministic Execution
        if active_tier in (SaaSPlanTier.TIER_1, SaaSPlanTier.TIER_2):
            session_obj = getattr(self._ctx, "session_state_obj", None)
            if session_obj:
                return self._ctx.execute_option(session_obj, raw_user_text)

        # 🧪 TIER 2.5 (BETA): Local NLM + Branch-and-Bound Engine
        if active_tier == SaaSPlanTier.TIER_2_5_BETA:
            return self._run_nlm_with_fallback(sanitized_text)

        # 🔴 TIER 3 (ENTERPRISE IN PRODUCTION): LLM -> NLM -> Branch-and-Bound
        return self._run_tier3_resilient_pipeline(sanitized_text)

    def _run_nlm_with_fallback(self, text: str) -> CommandResult:
        """Executes Local Machine Learning NLM classification with Branch-and-Bound fallback."""
        session_obj = getattr(self._ctx, "session_state_obj", None)
        if not session_obj:
            return CommandResult(success=False, message="No active session found.", action_type=ActionType.NAVIGATION)

        nlm_result = LocalNLMEngine.classify_intent(text)
        available_menu = self._ctx.get_available_menu(session_obj)

        if nlm_result.confidence_score >= self.CONFIDENCE_THRESHOLD:
            # Map NLM key to active menu choice
            matched_choice = self._map_nlm_key_to_menu(nlm_result.intent_key, available_menu)
            return self._ctx.execute_option(session_obj, matched_choice)

        # 🌳 FALLBACK: Branch-and-Bound Engine
        fallback_choice = BranchAndBoundEngine.resolve_state(text, available_menu)
        return self._ctx.execute_option(session_obj, fallback_choice)

    def _run_tier3_resilient_pipeline(self, text: str) -> CommandResult:
        """Tier 3 Pipeline: Primary LLM -> Secondary NLM -> Fallback Branch-and-Bound."""
        session_obj = getattr(self._ctx, "session_state_obj", None)
        if not session_obj:
            return CommandResult(success=False, message="No active session found.", action_type=ActionType.NAVIGATION)

        try:
            # 1. Primary: Simulate/Execute External LLM Call
            llm_choice = self._primary_llm_call(text)
            if llm_choice in self._ctx.get_available_menu(session_obj):
                return self._ctx.execute_option(session_obj, llm_choice)
            raise ValueError("LLM Returned choice outside active menu bounds.")
        except Exception:
            # 2. Secondary & Tertiary: Fallback to NLM + Branch-and-Bound
            return self._run_nlm_with_fallback(text)

    def _primary_llm_call(self, text: str) -> str:
        """Simulates primary LLM extraction logic."""
        if "simulate_offline" in text.lower():
            raise TimeoutError("External LLM API unreachable.")
        
        session_obj = getattr(self._ctx, "session_state_obj", None)
        menu = self._ctx.get_available_menu(session_obj) if session_obj else []
        return menu[0] if menu else "Exit Session"

    def _map_nlm_key_to_menu(self, nlm_key: str, menu: List[str]) -> str:
        """Maps NLM classification keys to active menu strings."""
        key_map = {
            "BRANCH_ROUTER": "Branch",
            "PRE_TRIAGE": "Triage",
            "TPA_INSURANCE": "Insurance",
            "SLOT_BOOKING": "Booking",
            "POST_CARE": "Post-Care",
        }
        target_substring = key_map.get(nlm_key, "")
        for option in menu:
            if target_substring in option:
                return option
        return menu[0] if menu else "Exit Session"

    def _ingress_guardrail(self, text: str) -> str:
        return re.sub(r"ignore\s+previous\s+instructions", "[REDACTED]", text, flags=re.IGNORECASE).strip()

    def _is_acute_emergency(self, text: str) -> bool:
        return any(kw in text.lower() for kw in ["uncontrolled bleeding", "jaw fracture", "knocked out tooth"])
