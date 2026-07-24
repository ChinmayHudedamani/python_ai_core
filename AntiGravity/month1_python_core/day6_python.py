import json
import os
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from day2_python import clean_client_data, mask_pii
from day4_python import generate_zero_hallucination_response
from day5_python import OfflineLedgerWriter

ALERTS_DIR: Path = Path(__file__).parent / "alerts"

def ensure_alerts_directory() -> None:
    """Ensures the local alerts directory exists for emergency and VIP HITL logs."""
    if not ALERTS_DIR.exists():
        ALERTS_DIR.mkdir(parents=True, exist_ok=True)


class SafetyCircuitBreaker:
    """
    Day 6 Enterprise Safety Circuit Breakers & Human-in-the-Loop (HITL) Manager.
    - Tier 1: Medical Emergency Override (112 National Emergency Referral)
    - Tier 2: VIP High-Revenue 15-Minute HITL Account Executive Dispatch
    """

    def __init__(self, ledger_writer: Optional[OfflineLedgerWriter] = None):
        ensure_alerts_directory()
        self.ledger: OfflineLedgerWriter = ledger_writer or OfflineLedgerWriter()

    def process_intake_safety_circuit(self, raw_patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes Day 6 Safety & HITL Circuit Pipeline over patient intake:
        1. RAG & Triage Evaluation (Day 4 Core)
        2. Emergency 112 Circuit Breaker Check
        3. VIP HITL Hand-off Alert Generation
        4. Idempotent Offline CSV Ledger Recording (Day 5)
        """
        response: Dict[str, Any] = generate_zero_hallucination_response(raw_patient_data)
        triage: Dict[str, Any] = response.get("triage", {})
        lead_tier: str = triage.get("lead_tier", "COLD_ROUTINE")
        patient: Dict[str, Any] = response.get("patient", {})

        timestamp_str: str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        circuit_status: Dict[str, Any] = {
            "circuit_action": "STANDARD_AUTOMATED_REPLY",
            "alert_file": None,
            "hitl_required": False
        }

        # 1. Tier 1: Medical Emergency Circuit Breaker (ESI RED)
        if lead_tier == "RED_CRITICAL_EMERGENCY":
            alert_filename = f"EMERGENCY_ALERT_{timestamp_str}.json"
            alert_path = ALERTS_DIR / alert_filename
            alert_payload = {
                "alert_type": "MEDICAL_EMERGENCY_ESI_RED",
                "severity": "CRITICAL",
                "patient_name": patient.get("name", "Unknown"),
                "phone": patient.get("phone", ""),
                "masked_phone": mask_pii(patient.get("phone", "")),
                "notes": patient.get("notes", ""),
                "action_required": "IMMEDIATE 112 EMERGENCY CALL / VISIT ER",
                "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }

            with open(alert_path, "w", encoding="utf-8") as f:
                json.dump(alert_payload, f, indent=2)

            circuit_status["circuit_action"] = "CRITICAL_112_OVERRIDE_TRIGGERED"
            circuit_status["alert_file"] = str(alert_path)
            circuit_status["hitl_required"] = True

        # 2. Tier 2: VIP High-Revenue HITL Account Executive Dispatch
        elif lead_tier == "VIP_HIGH_REVENUE":
            alert_filename = f"VIP_HITL_ALERT_{timestamp_str}.json"
            alert_path = ALERTS_DIR / alert_filename
            grounding = response.get("grounding_facts", {})
            doctors = grounding.get("matched_doctors", ["Dr. Chinmay Hudedamani"])
            
            alert_payload = {
                "alert_type": "VIP_HIGH_REVENUE_HITL_DISPATCH",
                "severity": "HIGH_PRIORITY_REVENUE",
                "patient_name": patient.get("name", "Unknown"),
                "phone": patient.get("phone", ""),
                "masked_phone": mask_pii(patient.get("phone", "")),
                "procedure_code": patient.get("procedure_code", "N/A"),
                "intent_score": triage.get("intent_score", 100),
                "assigned_doctor": doctors[0] if doctors else "Dr. Chinmay Hudedamani",
                "target_sla": "15-Minute Human Account Executive Callback",
                "available_slots": grounding.get("available_slots", []),
                "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }

            with open(alert_path, "w", encoding="utf-8") as f:
                json.dump(alert_payload, f, indent=2)

            circuit_status["circuit_action"] = "VIP_15MIN_HITL_DISPATCH_TRIGGERED"
            circuit_status["alert_file"] = str(alert_path)
            circuit_status["hitl_required"] = True

        # 3. Log to Offline Ledger
        ledger_result = self.ledger.log_patient_intake(response)
        response["circuit_status"] = circuit_status
        response["ledger_result"] = ledger_result

        return response


if __name__ == "__main__":
    print("==================================================")
    print("   DAY 6: SAFETY CIRCUIT BREAKER & HITL DEMO")
    print("==================================================\n")

    breaker = SafetyCircuitBreaker()

    test_cases = [
        {
            "title": "Medical Emergency (ESI RED 112 Circuit Breaker)",
            "data": {
                "name": "Rajesh Hegde",
                "phone": "+91-99000 11122",
                "procedure_code": "EMERGENCY",
                "notes": "Patient fell down, profuse bleeding and unconscious. Urgent emergency!"
            }
        },
        {
            "title": "VIP High-Revenue Lead (15-Min HITL AE Dispatch)",
            "data": {
                "name": "Ananya Roy",
                "phone": "+91-99887 76655",
                "procedure_code": "ALIGNERS",
                "notes": "Hi, what is the cost of invislin clear aligners in Bengaluru? Do you have EMI options?"
            }
        }
    ]

    for test in test_cases:
        print(f"--- TEST: {test['title']} ---")
        res = breaker.process_intake_safety_circuit(test["data"])
        print(json.dumps(res, indent=2))
        print("\n" + "="*50 + "\n")
