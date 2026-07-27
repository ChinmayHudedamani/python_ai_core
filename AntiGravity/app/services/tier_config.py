# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — 3-Tier SaaS Configuration Engine

from enum import Enum
from typing import List, Dict, Any, Set


class SaaSPlanTier(str, Enum):
    TIER_1 = "TIER_1_ESSENTIAL"
    TIER_2 = "TIER_2_PRO"
    TIER_3 = "TIER_3_ENTERPRISE"


# Informational options across ALL tiers that MUST be permanently hidden once viewed
INFORMATIONAL_OPTIONS: Set[str] = {
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
}


TIER_CAPABILITIES: Dict[SaaSPlanTier, Dict[str, Any]] = {
    SaaSPlanTier.TIER_1: {
        "name": "Tier 1: Essential (24/7 Digital Receptionist)",
        "menu": [
            "🌐 0. Select Language (English / Kannada / Hindi)",
            "1. Doctor Details",
            "2. Clinic Timings & Live Status",
            "3. Location & Valet Parking",
            "4. Cost Ranges & Pricing Sheet",
            "5. Sterilization & Safety Protocols",
            "6. Patient Reviews",
            "7. 🚨 Dental Emergency (Call Now)",
            "8. Exit Session"
        ],
        "features": {
            "has_live_status_clock": True,
            "has_pricing_disclaimer": True,
            "has_emergency_tap_to_call": True,
            "has_live_slots": False,
            "has_otp_auth": False,
            "has_surgical_priority": False,
            "has_pre_triage": False,
            "has_tpa_insurance": False,
            "has_multi_branch": False,
            "has_lead_recovery": False,
            "has_doctor_command_center": False
        }
    },
    SaaSPlanTier.TIER_2: {
        "name": "Tier 2: Pro (Revenue & Schedule Guard)",
        "menu": [
            "1. Doctor Details",
            "2. Clinic Timings & Location",
            "3. Cost Ranges & Pricing Sheet",
            "4. 📅 Book Appointment (Live Slots)",
            "5. 🔄 Reschedule / Cancel Appointment",
            "6. Patient Reviews",
            "7. 🚨 Emergency Triage",
            "8. Exit Session"
        ],
        "features": {
            "has_live_status_clock": True,
            "has_pricing_disclaimer": True,
            "has_emergency_tap_to_call": True,
            "has_live_slots": True,
            "has_otp_auth": True,
            "has_surgical_priority": True,  # OPERATION_SURGERY > GENERAL_CONSULTATION
            "has_checkin_codes": True,      # APX-XXXX Generation
            "has_pre_triage": False,
            "has_tpa_insurance": False,
            "has_multi_branch": False,
            "has_lead_recovery": False,
            "has_doctor_command_center": False
        }
    },
    SaaSPlanTier.TIER_3: {
        "name": "Tier 3: Enterprise (Apollo/Fortis-Grade Concierge)",
        "menu": [
            "🏥 1. Select Clinic Branch & Specialist",
            "🩺 2. Guided Clinical Pre-Triage",
            "💳 3. Cashless TPA Insurance Desk",
            "📋 4. Post-Care & Recall Rules",
            "📅 5. Interactive Slot Booking (Priority Engine)",
            "⭐ 6. Reviews & Feedback",
            "❌ 7. Exit Session"
        ],
        "features": {
            "has_live_status_clock": True,
            "has_pricing_disclaimer": True,
            "has_emergency_tap_to_call": True,
            "has_live_slots": True,
            "has_otp_auth": True,
            "has_surgical_priority": True,
            "has_checkin_codes": True,
            "has_pre_triage": True,
            "has_tpa_insurance": True,       # Provider lookup + Document photo upload + Co-pay estimate
            "has_multi_branch": True,       # Branch & specialist routing
            "has_lead_recovery": True,      # Abandoned high-ticket session tracker
            "has_doctor_command_center": True # OT emergency schedule override tool
        }
    }
}
