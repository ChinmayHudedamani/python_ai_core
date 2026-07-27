import json
import math
import os
import random
from pathlib import Path
from typing import Dict, Any, List, Tuple

WEIGHTS_FILE = Path(__file__).parent / "rl_policy_weights.json"

STRATEGIES = [
    "STRATEGY_INFORM_PRICE_EMI",
    "STRATEGY_HIGHLIGHT_DOCTOR",
    "STRATEGY_CHECK_TIMING",
    "STRATEGY_COLLECT_NAME",
    "STRATEGY_COLLECT_PHONE"
]


class ContextualBanditRLPolicyEngine:
    """Contextual Bandit RL Policy Engine for Dynamic Conversation Strategy Selection."""

    def __init__(self, epsilon: float = 0.1, alpha: float = 0.1):
        self.epsilon = epsilon
        self.alpha = alpha
        self.weights: Dict[str, Dict[str, float]] = self._load_weights()
        self.counts: Dict[str, Dict[str, int]] = {s: {k: 1 for k in ["total"]} for s in STRATEGIES}

    def _load_weights(self) -> Dict[str, Dict[str, float]]:
        if WEIGHTS_FILE.exists():
            try:
                with open(WEIGHTS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        # Initial baseline Q-values for actions across contexts
        return {
            s: {
                "price_query": 0.8 if s == "STRATEGY_INFORM_PRICE_EMI" else 0.4,
                "doctor_query": 0.8 if s == "STRATEGY_HIGHLIGHT_DOCTOR" else 0.4,
                "timing_query": 0.8 if s == "STRATEGY_CHECK_TIMING" else 0.4,
                "missing_name": 0.9 if s == "STRATEGY_COLLECT_NAME" else 0.2,
                "missing_phone": 0.9 if s == "STRATEGY_COLLECT_PHONE" else 0.2,
                "default": 0.5
            }
            for s in STRATEGIES
        }

    def save_weights(self) -> None:
        try:
            with open(WEIGHTS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.weights, f, indent=2)
        except Exception:
            pass

    def extract_context_key(self, context: Dict[str, Any]) -> str:
        if not context.get("has_name"):
            return "missing_name"
        if context.get("is_booking_intent") and not context.get("has_phone"):
            return "missing_phone"
        if context.get("is_price_query"):
            return "price_query"
        if context.get("is_doctor_query"):
            return "doctor_query"
        if context.get("is_timing_query"):
            return "timing_query"
        return "default"

    def select_action(self, context: Dict[str, Any]) -> Tuple[str, float]:
        ctx_key = self.extract_context_key(context)

        # Epsilon-greedy exploration vs exploitation
        if random.random() < self.epsilon:
            chosen = random.choice(STRATEGIES)
            return chosen, self.weights.get(chosen, {}).get(ctx_key, 0.5)

        # UCB1 (Upper Confidence Bound) strategy selection
        best_strategy = STRATEGIES[0]
        best_score = -1.0

        total_pulls = sum(self.counts[s].get("total", 1) for s in STRATEGIES)

        for s in STRATEGIES:
            q_val = self.weights.get(s, {}).get(ctx_key, 0.5)
            n_pulls = self.counts[s].get("total", 1)
            bonus = math.sqrt((2 * math.log(total_pulls + 1)) / n_pulls)
            score = q_val + 0.1 * bonus
            if score > best_score:
                best_score = score
                best_strategy = s

        return best_strategy, round(best_score, 4)

    def update_policy(self, strategy: str, context: Dict[str, Any], reward: float) -> None:
        """Temporal Difference Q-Value update based on environment reward."""
        ctx_key = self.extract_context_key(context)
        if strategy not in self.weights:
            self.weights[strategy] = {}

        old_q = self.weights[strategy].get(ctx_key, 0.5)
        new_q = old_q + self.alpha * (reward - old_q)
        self.weights[strategy][ctx_key] = round(new_q, 4)

        if strategy not in self.counts:
            self.counts[strategy] = {"total": 1}
        self.counts[strategy]["total"] = self.counts[strategy].get("total", 1) + 1

        self.save_weights()
