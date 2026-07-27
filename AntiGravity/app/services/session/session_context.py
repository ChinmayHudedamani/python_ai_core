# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Session Context Manager and Factory Registry

import logging
from typing import Dict, List, Optional

from app.services.session.models import PatientSession, CommandResult, ActionType
from app.services.session.base_strategy import AbstractTierStrategy
from app.services.session.tier1_strategy import Tier1Strategy
from app.services.session.tier2_strategy import Tier2Strategy
from app.services.session.tier3_strategy import Tier3Strategy
from app.services.tier_config import SaaSPlanTier
from app.services.session_manager import InputSanitizationPipeline, SecurityViolationException, StructuredJsonLogger
from app.services.security import IngressSanitizer

logger = logging.getLogger("APEX_SESSION_CONTEXT")


class SessionContextManager:
    """Factory Registry and Context Manager eliminating if/else branching for SaaS tier execution."""

    def __init__(self):
        # Factory Registry mapping Enums to strategy singleton instances
        self._strategy_registry: Dict[SaaSPlanTier, AbstractTierStrategy] = {
            SaaSPlanTier.TIER_1: Tier1Strategy(),
            SaaSPlanTier.TIER_2: Tier2Strategy(),
            SaaSPlanTier.TIER_3: Tier3Strategy()
        }
        self.telemetry = StructuredJsonLogger()

    def get_strategy(self, tier: SaaSPlanTier) -> AbstractTierStrategy:
        """Resolves tier strategy via $O(1)$ Factory Registry lookup."""
        return self._strategy_registry.get(tier, self._strategy_registry[SaaSPlanTier.TIER_1])

    def set_tier(self, session: PatientSession, target_tier: SaaSPlanTier) -> SaaSPlanTier:
        """Enables seamless live tier switching without losing session state or phone identification."""
        session.active_tier = target_tier
        self.telemetry.log_event("TIER_SWITCHED", session.session_id, {
            "target_tier": target_tier.value,
            "phone_number": session.phone_number
        })
        return session.active_tier

    def get_available_menu(self, session: PatientSession) -> List[str]:
        """Returns filtered available menu for the active session and tier."""
        strategy = self.get_strategy(session.active_tier)
        return strategy.get_menu(session)

    def execute_option(self, session: PatientSession, raw_input: str) -> CommandResult:
        """Sanitizes input, resolves tier strategy, and executes command via Dispatcher Map."""
        if not session.is_active:
            return CommandResult(
                success=False,
                message="⚠️ Session is closed. Please start a new session.",
                action_type=ActionType.NAVIGATION
            )

        try:
            # Step 1: OWASP Security Ingress Sanitization & Unicode Normalization
            normalized_input = IngressSanitizer.sanitize_choice(raw_input)
            clean_text = InputSanitizationPipeline.sanitize(normalized_input)
        except SecurityViolationException as e:
            self.telemetry.log_event("SECURITY_VIOLATION_BLOCKED", session.session_id, {"raw_input": raw_input})
            return CommandResult(
                success=False,
                message=f"🚨 SECURITY BLOCK: {str(e)}",
                action_type=ActionType.SECURITY_BLOCK
            )

        # Step 2: Resolve Strategy via Factory Registry ($O(1)$ lookup)
        strategy = self.get_strategy(session.active_tier)

        # Step 3: Execute Option via Strategy Dispatcher
        result = strategy.process_option(session, clean_text)

        # Step 4: Audit Telemetry Logging
        self.telemetry.log_event("STRATEGY_EXECUTED", session.session_id, {
            "tier": session.active_tier.value,
            "choice": clean_text,
            "success": result.success,
            "action_type": result.action_type.value,
            "hidden_count": len(session.hidden_options)
        })

        return result
