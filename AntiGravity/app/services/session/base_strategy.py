# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Abstract Base Tier Strategy Interface

from abc import ABC, abstractmethod
from typing import List, Dict, Callable

from app.services.session.models import PatientSession, CommandResult, ActionType
from app.services.tier_config import SaaSPlanTier, INFORMATIONAL_OPTIONS, TIER_CAPABILITIES


class AbstractTierStrategy(ABC):
    """Abstract Strategy interface for SaaS tier menu generation and execution handling."""

    def __init__(self, tier: SaaSPlanTier):
        self.tier = tier
        self._dispatcher_map: Dict[str, Callable[[PatientSession, str], CommandResult]] = self._build_dispatcher_map()

    @abstractmethod
    def _build_dispatcher_map(self) -> Dict[str, Callable[[PatientSession, str], CommandResult]]:
        """Builds dictionary dispatcher mapping menu items to strategy handler methods."""
        pass

    def get_menu(self, session: PatientSession) -> List[str]:
        """Returns menu list filtered of previously viewed informational options using set difference."""
        tier_data = TIER_CAPABILITIES.get(self.tier, TIER_CAPABILITIES[SaaSPlanTier.TIER_1])
        full_menu = list(tier_data["menu"])
        return [item for item in full_menu if item not in session.hidden_options]

    def process_option(self, session: PatientSession, option_text: str) -> CommandResult:
        """Executes choice via $O(1)$ Dispatcher Map or falls back to transactional handler."""
        available = self.get_menu(session)
        if option_text not in available:
            return CommandResult(
                success=False,
                message=f"⚠️ Option '{option_text}' is not available or already hidden for this session. Scroll up to review previous details.",
                action_type=ActionType.INFORMATIONAL
            )

        # Dispatch execution through handler map
        handler = self._dispatcher_map.get(option_text, self._default_transactional_handler)
        return handler(session, option_text)

    def _default_transactional_handler(self, session: PatientSession, option_text: str) -> CommandResult:
        """Fallback handler for unmapped transactional choices."""
        return CommandResult(
            success=True,
            message=f"⚙️ Interactive action initiated for [{option_text}].",
            action_type=ActionType.TRANSACTIONAL
        )

    def _handle_informational_option(self, session: PatientSession, option_text: str, detail_body: str) -> CommandResult:
        """Common helper for informational options enforcing the Read Once & Scroll Up rule."""
        session.hidden_options.add(option_text)
        disclaimer = (
            "\n\n📌 *Note: Standard price estimates. Dr. Chinmay Hudedamani will evaluate exact cost in person.*"
            if "Cost" in option_text or "Pricing" in option_text else ""
        )
        msg = (
            f"ℹ️ [{option_text}]\n{detail_body}{disclaimer}\n\n"
            f"📌 *Note: This option is now hidden. Scroll up anytime in WhatsApp to re-read these details.*"
        )
        return CommandResult(
            success=True,
            message=msg,
            action_type=ActionType.INFORMATIONAL
        )
