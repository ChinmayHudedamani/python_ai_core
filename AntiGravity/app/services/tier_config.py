# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Enterprise 3-Tier SaaS Configuration Engine

from enum import Enum
from typing import Dict, Any, Final, FrozenSet


class SaaSPlanTier(str, Enum):
    """SaaS Subscription Tiers defining capability escalation levels."""
    TIER_1 = "TIER_1_ESSENTIAL"
    TIER_2 = "TIER_2_PRO"
    TIER_3 = "TIER_3_ENTERPRISE"


class MenuOptionCategory(str, Enum):
    """Categorization of menu items for strategy routing."""
    INFORMATIONAL = "INFORMATIONAL"
    TRANSACTIONAL = "TRANSACTIONAL"
    EMERGENCY = "EMERGENCY"
    NAVIGATION = "NAVIGATION"


# Immutable FrozenSet of Informational Options that MUST be permanently hidden once viewed
INFORMATIONAL_OPTIONS: Final[FrozenSet[str]] = frozenset({
    # Tier 1 Info Options
    "1. Doctor Details",
    "2. Clinic Timings & Live Status",
    "3. Location & Valet Parking",
    "4. Cost Ranges & Pricing Sheet",
    "5. Sterilization & Safety Protocols",
    "6. Patient Reviews",
    
    # Tier 2 Info Options
    "1. Doctor Details",
    "2. Clinic Timings & Location",
    "3. Cost Ranges & Pricing Sheet",
    "6. Patient Reviews",
    
    # Tier 3 Info Options
    "💳 3. Cashless TPA Insurance Desk",
    "📋 4. Post-Care & Recall Rules",
    "⭐ 6. Reviews & Feedback"
})


TIER_CAPABILITIES: Final[Dict[SaaSPlanTier, Dict[str, Any]]] = {
    SaaSPlanTier.TIER_1: {
        "name": "Tier 1: Essential (24/7 Digital Receptionist)",
        "menu": (
            "🌐 0. Select Language (English / Kannada / Hindi)",
            "1. Doctor Details",
            "2. Clinic Timings & Live Status",
            "3. Location & Valet Parking",
            "4. Cost Ranges & Pricing Sheet",
            "5. Sterilization & Safety Protocols",
            "6. Patient Reviews",
            "7. 🚨 Dental Emergency (Call Now)",
            "8. Exit Session"
        ),
        "features": frozenset({
            "has_live_status_clock",
            "has_pricing_disclaimer",
            "has_emergency_tap_to_call"
        })
    },
    SaaSPlanTier.TIER_2: {
        "name": "Tier 2: Pro (Revenue & Schedule Guard)",
        "menu": (
            "1. Doctor Details",
            "2. Clinic Timings & Location",
            "3. Cost Ranges & Pricing Sheet",
            "4. 📅 Book Appointment (Live Slots)",
            "5. 🔄 Reschedule / Cancel Appointment",
            "6. Patient Reviews",
            "7. 🚨 Emergency Triage",
            "8. Exit Session"
        ),
        "features": frozenset({
            "has_live_status_clock",
            "has_pricing_disclaimer",
            "has_emergency_tap_to_call",
            "has_live_slots",
            "has_otp_auth",
            "has_surgical_priority",
            "has_checkin_codes"
        })
    },
    SaaSPlanTier.TIER_3: {
        "name": "Tier 3: Enterprise (Apollo/Fortis-Grade Concierge)",
        "menu": (
            "🏥 1. Select Clinic Branch & Specialist",
            "🩺 2. Guided Clinical Pre-Triage",
            "💳 3. Cashless TPA Insurance Desk",
            "📋 4. Post-Care & Recall Rules",
            "📅 5. Interactive Slot Booking (Priority Engine)",
            "⭐ 6. Reviews & Feedback",
            "❌ 7. Exit Session"
        ),
        "features": frozenset({
            "has_live_status_clock",
            "has_pricing_disclaimer",
            "has_emergency_tap_to_call",
            "has_live_slots",
            "has_otp_auth",
            "has_surgical_priority",
            "has_checkin_codes",
            "has_pre_triage",
            "has_tpa_insurance",
            "has_multi_branch",
            "has_lead_recovery",
            "has_doctor_command_center"
        })
    }
}
