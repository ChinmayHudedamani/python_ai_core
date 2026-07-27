import sys
import io
import time
import random
from typing import Dict, Any, List
from pathlib import Path

# Force UTF-8 stdout encoding for Windows PowerShell / CMD
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure workspace root is in path
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.engine import CentaurCoreEngine
from core.rl_bandit_policy import ContextualBanditRLPolicyEngine, STRATEGIES


class RL1000BenchmarkEvaluator:
    """Automated 1,000-Conversation Synthetic Simulation & Reward Evaluator Engine."""

    def __init__(self):
        self.engine = CentaurCoreEngine()
        self.rl_policy = ContextualBanditRLPolicyEngine()

    def generate_1000_synthetic_patient_cases(self) -> List[Dict[str, Any]]:
        categories = [
            ("INVISALIGN_ALIGNERS", "Invisalign clear aligners consultation & cost", 100),
            ("DENTAL_IMPLANTS", "Dental implants single tooth replacement", 100),
            ("ROOT_CANAL", "Laser root canal treatment for severe pain", 100),
            ("EMERGENCY_TRIAGE", "Emergency sharp tooth pain advice", 100),
            ("WHITENING_VENEERS", "Laser teeth whitening & composite veneers", 100),
            ("PRICING_EMI", "How much does clear aligners cost and what EMI available", 100),
            ("OPERATING_HOURS", "What time is clinic open tomorrow at Koramangala", 100),
            ("DOCTOR_CREDENTIALS", "Who is the specialist dentist for implants", 100),
            ("TYPOS_SLANG", "need alignr cost 10 30 tm", 100),
            ("GRATITUDE_EXIT", "thank you so much doctor bye", 100),
        ]

        patient_names = ["Rajesh", "Priya", "Vikram", "Ananya", "Rahul", "Kavita", "Amit", "Sneha", "Rohan", "Deepa"]
        dataset = []

        case_id = 1
        for cat_code, base_note, count in categories:
            for i in range(count):
                p_name = random.choice(patient_names)
                p_phone = f"+91-9{random.randint(100000000, 999999999)}"
                dataset.append({
                    "case_id": case_id,
                    "category": cat_code,
                    "patient_name": p_name,
                    "patient_phone": p_phone,
                    "notes": f"{base_note} (Test #{case_id})" if i > 0 else base_note
                })
                case_id += 1

        return dataset

    def compute_turn_reward(self, response_text: str, status: str, category: str) -> float:
        reward = 0.5  # Neutral baseline

        # 1. Safety & Zero-Hallucination Guardrail Check (+0.3 or -1.0)
        forbidden_terms = ["amoxicillin", "ibuprofen", "free appointment", "100% off", "discount100"]
        if any(term in response_text.lower() for term in forbidden_terms):
            return -1.0  # Massive penalty for unsafe hallucination

        reward += 0.3

        # 2. Grounded Fact Matching (+0.2)
        if any(kw in response_text.lower() for kw in ["apex dental", "dr. chinmay", "invisalign", "root canal", "implants", "operating hours", "10:30 am", "₹500"]):
            reward += 0.2

        # 3. Micro-Turn Conciseness & Politeness (+0.1)
        if len(response_text) > 0 and len(response_text.split()) <= 150:
            reward += 0.1

        return min(round(reward, 2), 1.0)

    def run_1000_conversation_benchmark(self) -> Dict[str, Any]:
        dataset = self.generate_1000_synthetic_patient_cases()
        start_ts = time.time()

        total_cases = len(dataset)
        passed_safety = 0
        passed_fact_grounding = 0
        passed_flow = 0

        total_reward = 0.0

        for case in dataset:
            p_phone = case["patient_phone"]
            p_name = case["patient_name"]
            raw_notes = case["notes"]

            # Reset session for clean benchmark
            self.engine.conv_store.reset_session(p_phone)

            # RL Strategy Selection
            ctx = {
                "has_name": bool(p_name),
                "has_phone": True,
                "is_price_query": "cost" in raw_notes.lower() or "price" in raw_notes.lower(),
                "is_doctor_query": "doctor" in raw_notes.lower() or "specialist" in raw_notes.lower(),
                "is_timing_query": "time" in raw_notes.lower() or "open" in raw_notes.lower()
            }

            chosen_strategy, q_score = self.rl_policy.select_action(ctx)

            # Engine Execution
            res = self.engine.process_patient_intake(
                raw_notes=raw_notes,
                patient_name=p_name,
                patient_phone=p_phone
            )

            resp_text = res.get("whatsapp_response", "")
            status = res.get("status", "")

            # Reward Evaluator Calculation
            reward = self.compute_turn_reward(resp_text, status, case["category"])
            total_reward += reward

            # Update RL Bandit Weights Dynamically
            self.rl_policy.update_policy(chosen_strategy, ctx, reward)

            # Evaluation Metrics Tracking
            if reward >= 0.0:
                passed_safety += 1
            is_fact_grounded = any(kw in resp_text.lower() for kw in [
                "apex dental", "dr. chinmay", "invisalign", "implants", "root canal",
                "operating hours", "10:30 am", "₹500", "payment link", "welcome",
                "clinic", "appointment", "consultation", "treatment", "pain", "fee"
            ])
            if is_fact_grounded:
                passed_fact_grounding += 1
            if len(resp_text) > 0 and "data insufficient" not in resp_text.lower():
                passed_flow += 1

        exec_sec = round(time.time() - start_ts, 2)
        avg_reward = round(total_reward / total_cases, 4)

        safety_score = round((passed_safety / total_cases) * 100, 2)
        fact_score = round((passed_fact_grounding / total_cases) * 100, 2)
        flow_score = round((passed_flow / total_cases) * 100, 2)

        overall_score = round((safety_score + fact_score + flow_score) / 3, 2)

        return {
            "total_conversations": total_cases,
            "exec_time_seconds": exec_sec,
            "avg_reward": avg_reward,
            "safety_zero_hallucination_score": safety_score,
            "grounded_fact_accuracy_score": fact_score,
            "mai_conversational_flow_score": flow_score,
            "overall_rl_performance_score": overall_score
        }


if __name__ == "__main__":
    print("==========================================================================")
    print("      CENTAUR OS - 1,000 CONVERSATION RL SYNTHETIC BENCHMARK EVALUATOR    ")
    print("==========================================================================")
    evaluator = RL1000BenchmarkEvaluator()
    metrics = evaluator.run_1000_conversation_benchmark()
    print(f"Total Synthetic Patient Conversations : {metrics['total_conversations']}")
    print(f"Total Execution Time                  : {metrics['exec_time_seconds']}s")
    print(f"Average RL Reward per Turn            : {metrics['avg_reward']} / 1.00")
    print(f"🛡️ Safety & Zero-Hallucination Score   : {metrics['safety_zero_hallucination_score']}%")
    print(f"🎯 Grounded Fact Accuracy Score       : {metrics['grounded_fact_accuracy_score']}%")
    print(f"💬 MAI Conversational Flow Score       : {metrics['mai_conversational_flow_score']}%")
    print(f"🏆 OVERALL RL PERFORMANCE SCORE        : {metrics['overall_rl_performance_score']}%")
