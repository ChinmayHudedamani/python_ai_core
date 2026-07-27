# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — NLM & Tri-Layer Resilient Gateway Verification Test Suite

import sys
import unittest
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.session.models import PatientSession, SaaSPlanTier
from app.services.session.session_context import SessionContextManager
from app.services.nlm_engine import LocalNLMEngine, BranchAndBoundEngine, IntentCandidate
from app.services.ai_sandwich import AISandwichEngine


class TestNLMTriLayerResilience(unittest.TestCase):

    def setUp(self):
        self.context_mgr = SessionContextManager()
        self.session = PatientSession(
            session_id="SESS_TRI_LAYER",
            phone_number="+919876543210",
            active_tier=SaaSPlanTier.TIER_3
        )
        self.context_mgr.session_state_obj = self.session
        self.sandwich = AISandwichEngine(self.context_mgr)

    def test_01_local_nlm_classification(self):
        print("\n--- [TEST 1]: Local NLM Engine Intent Vector Classification ---")
        candidate: IntentCandidate = LocalNLMEngine.classify_intent("I have severe toothache and swelling")
        self.assertEqual(candidate.intent_key, "PRE_TRIAGE")
        self.assertGreater(candidate.confidence_score, 0.3)
        self.assertEqual(candidate.urgency_bound, 0.8)

        candidate_tpa = LocalNLMEngine.classify_intent("Star Health cashless insurance claim policy")
        self.assertEqual(candidate_tpa.intent_key, "TPA_INSURANCE")
        print("✅ PASSED: Local NLM Engine classified PRE_TRIAGE and TPA_INSURANCE correctly.")

    def test_02_branch_and_bound_heuristics(self):
        print("\n--- [TEST 2]: Branch-and-Bound Heuristic Bounding Function f(n) ---")
        menu = [
            "🏥 1. Select Clinic Branch & Specialist",
            "🩺 2. Guided Clinical Pre-Triage",
            "💳 3. Cashless TPA Insurance Desk",
            "📋 4. Post-Care & Recall Rules",
            "📅 5. Interactive Slot Booking (Priority Engine)",
        ]
        
        resolved_triage = BranchAndBoundEngine.resolve_state("severe pain and toothache", menu)
        self.assertEqual(resolved_triage, "🩺 2. Guided Clinical Pre-Triage")

        resolved_insurance = BranchAndBoundEngine.resolve_state("cashless claim policy card", menu)
        self.assertEqual(resolved_insurance, "💳 3. Cashless TPA Insurance Desk")
        print("✅ PASSED: Branch-and-Bound Engine resolved candidate states using f(n) bounds.")

    def test_03_tri_layer_llm_to_nlm_fallback(self):
        print("\n--- [TEST 3]: Tri-Layer Gateway: Primary LLM -> Secondary NLM -> Fallback ---")
        # Simulating external LLM API failure / offline mode
        res = self.sandwich.process_patient_input("simulate_offline cashless insurance claim")
        self.assertTrue(res.success)
        self.assertIn("Cashless TPA Insurance Desk", res.message)
        print("✅ PASSED: Primary LLM failure successfully fell back to NLM & Branch-and-Bound!")


if __name__ == "__main__":
    unittest.main()
