# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# Copus AI Chatbot — Phase 1: 3-Tier Core Session State Machine

import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from app.services.tier_config import SaaSPlanTier, INFORMATIONAL_OPTIONS, TIER_CAPABILITIES


@dataclass
class PatientSession:
    phone_number: str
    active_tier: SaaSPlanTier = SaaSPlanTier.TIER_1
    hidden_options: List[str] = field(default_factory=list)
    selected_language: str = "English"

    def get_available_menu(self) -> List[str]:
        """Returns active menu filtered of all previously viewed informational options."""
        tier_info = TIER_CAPABILITIES.get(self.active_tier, TIER_CAPABILITIES[SaaSPlanTier.TIER_1])
        full_menu = tier_info["menu"]
        return [item for item in full_menu if item not in self.hidden_options]

    def process_selection(self, selected_option: str) -> str:
        """Handles selection, hides info options immediately, and returns token-efficient response."""
        available = self.get_available_menu()
        if selected_option not in available:
            return f"⚠️ Option already viewed or unavailable. Please scroll up to review previous details."

        # Core Rule: Permanently hide any informational selection for this session
        if selected_option in INFORMATIONAL_OPTIONS:
            self.hidden_options.append(selected_option)
            return (
                f"ℹ️ [Information Displayed for: {selected_option}]\n"
                f"📌 *Note: This option is now hidden. Scroll up anytime to re-read these details.*"
            )

        if "Exit" in selected_option:
            return "👋 Thank you for contacting us. Session closed."

        return f"⚡ Action initiated for: {selected_option}"


# --- Local Terminal Test Runner ---
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Copus AI — 3-Tier Session Manager Test Suite")
    print("=" * 60)

    # 1. Test Tier 1 Essential
    session_t1 = PatientSession(phone_number="+919876543210", active_tier=SaaSPlanTier.TIER_1)
    print("\n--- [TEST TIER 1 ESSENTIAL] ---")
    print(f"Initial TIER_1 Menu Count: {len(session_t1.get_available_menu())}")
    res_t1 = session_t1.process_selection("1. Doctor Details")
    print(f"Bot Output:\n{res_t1}")
    print(f"Menu Count After Selection: {len(session_t1.get_available_menu())}")
    assert "1. Doctor Details" not in session_t1.get_available_menu()
    print("✅ TIER_1 Test PASSED: '1. Doctor Details' hidden successfully.")

    # 2. Test Tier 2 Pro
    session_t2 = PatientSession(phone_number="+919876543211", active_tier=SaaSPlanTier.TIER_2)
    print("\n--- [TEST TIER 2 PRO] ---")
    print(f"Initial TIER_2 Menu Count: {len(session_t2.get_available_menu())}")
    res_t2 = session_t2.process_selection("3. Cost Ranges & Pricing Sheet")
    print(f"Bot Output:\n{res_t2}")
    print(f"Menu Count After Selection: {len(session_t2.get_available_menu())}")
    assert "3. Cost Ranges & Pricing Sheet" not in session_t2.get_available_menu()
    print("✅ TIER_2 Test PASSED: '3. Cost Ranges & Pricing Sheet' hidden successfully.")

    # 3. Test Tier 3 Enterprise
    session_t3 = PatientSession(phone_number="+919876543212", active_tier=SaaSPlanTier.TIER_3)
    print("\n--- [TEST TIER 3 ENTERPRISE] ---")
    print(f"Initial TIER_3 Menu Count: {len(session_t3.get_available_menu())}")
    res_t3 = session_t3.process_selection("💳 3. Cashless TPA Insurance Desk")
    print(f"Bot Output:\n{res_t3}")
    print(f"Menu Count After Selection: {len(session_t3.get_available_menu())}")
    assert "💳 3. Cashless TPA Insurance Desk" not in session_t3.get_available_menu()
    print("✅ TIER_3 Test PASSED: '💳 3. Cashless TPA Insurance Desk' hidden successfully.")

    print("\n🎉 ALL 3-TIER SESSION MANAGER TESTS PASSED 100%!")