# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Session Strategy Enums and Dataclasses

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Set, Dict, Any, Optional, Final, FrozenSet

from app.services.tier_config import SaaSPlanTier, INFORMATIONAL_OPTIONS


class ActionType(str, Enum):
    """Classification of execution command results."""
    INFORMATIONAL = "INFORMATIONAL"
    TRANSACTIONAL = "TRANSACTIONAL"
    EMERGENCY = "EMERGENCY"
    NAVIGATION = "NAVIGATION"
    SECURITY_BLOCK = "SECURITY_BLOCK"
    UPGRADE_PROMPT = "UPGRADE_PROMPT"


class PriorityLevel(str, Enum):
    """Clinical priority hierarchy for slot scheduling and collision resolution."""
    SURGICAL_PRIORITY = "SURGICAL_PRIORITY"
    GENERAL_CONSULTATION = "GENERAL_CONSULTATION"
    ACUTE_EMERGENCY = "ACUTE_EMERGENCY"


class ProcedureType(str, Enum):
    """Dental clinical procedure classification."""
    EXTRACTION = "EXTRACTION"
    ROOT_CANAL = "ROOT_CANAL"
    ALIGNERS = "ALIGNERS"
    IMPLANTS = "IMPLANTS"
    GENERAL = "GENERAL"


@dataclass(slots=True)
class CommandResult:
    """Immutable result structure emitted by Strategy dispatchers."""
    success: bool
    message: str
    action_type: ActionType
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PatientSession:
    """Memory-optimized slots-backed patient session state container."""
    session_id: str
    phone_number: str
    active_tier: SaaSPlanTier = SaaSPlanTier.TIER_1
    hidden_options: Set[str] = field(default_factory=set)
    is_authenticated: bool = False
    selected_language: str = "English"
    selected_branch: str = "Yelahanka Node v0.2"
    selected_specialist: str = "Dr. Chinmay Hudedamani (MDS)"
    selected_tpa_insurance: Optional[str] = None
    otp_code: Optional[str] = None
    check_in_code: Optional[str] = None
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def mark_option_hidden(self, option_text: str):
        """Adds option to hidden_options set."""
        self.hidden_options.add(option_text)

    def reset_hidden_options(self):
        """Clears hidden options list."""
        self.hidden_options.clear()
