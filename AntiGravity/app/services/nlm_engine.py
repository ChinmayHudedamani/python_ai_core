# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Local NLM Intent Classifier & Branch-and-Bound State Engine

import math
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Final


@dataclass(slots=True, frozen=True)
class IntentCandidate:
    """Memory-optimized frozen slots dataclass for NLM intent scoring."""
    intent_key: str
    confidence_score: float
    urgency_bound: float


class LocalNLMEngine:
    """Lightweight Local Natural Language Modeling (NLM) & Intent Classifier."""

    INTENT_VECTORS: Final[Dict[str, List[str]]] = {
        "BRANCH_ROUTER": ["branch", "location", "koramangala", "yelahanka", "indiranagar", "specialist", "where"],
        "PRE_TRIAGE": ["pain", "swelling", "ache", "toothache", "bleeding", "emergency", "triage", "symptom", "hurt"],
        "TPA_INSURANCE": ["insurance", "tpa", "claim", "star health", "hdfc", "cashless", "coverage", "policy"],
        "SLOT_BOOKING": ["book", "appointment", "slot", "reserve", "schedule", "timing", "consultation"],
        "POST_CARE": ["care", "post-op", "extraction", "root canal", "instructions", "recovery", "after"],
    }

    @classmethod
    def classify_intent(cls, text: str) -> IntentCandidate:
        """Classifies text using keyword feature vectors and normalized scoring."""
        tokens = text.lower().split()
        if not tokens:
            return IntentCandidate("UNKNOWN", 0.0, 0.0)

        best_intent = "UNKNOWN"
        max_score = 0.0

        for intent, keywords in cls.INTENT_VECTORS.items():
            matches = sum(1 for token in tokens if any(kw in token for kw in keywords))
            score = matches / (len(tokens) + 1)
            if score > max_score:
                max_score = score
                best_intent = intent

        urgency = 0.8 if any(k in text.lower() for k in ["pain", "bleed", "severe", "swelling"]) else 0.2
        return IntentCandidate(
            intent_key=best_intent,
            confidence_score=min(max_score * 2.5, 1.0),
            urgency_bound=urgency
        )


class BranchAndBoundEngine:
    """
    Finite Group & Branch-and-Bound State Decision Engine.
    Used when both LLM and NLM confidence bounds fall below operational thresholds.
    """

    @classmethod
    def resolve_state(cls, input_text: str, available_menu: List[str]) -> str:
        """
        Executes Branch-and-Bound Search across candidate menu states.
        Branching: Expands all available menu items.
        Bounding: Evaluates heuristic bound score f(node) to select optimal state.
        """
        if not available_menu:
            return "Exit Session"

        best_node = available_menu[0]
        upper_bound = -100.0

        for candidate in available_menu:
            bound_score = cls._calculate_bound_score(input_text, candidate)
            if bound_score > upper_bound:
                upper_bound = bound_score
                best_node = candidate

        return best_node

    @staticmethod
    def _calculate_bound_score(input_text: str, candidate_option: str) -> float:
        """Heuristic Bounding Function f(n) evaluating candidate fit."""
        tokens = set(input_text.lower().split())
        candidate_tokens = set(candidate_option.lower().split())

        overlap = len(tokens.intersection(candidate_tokens))
        
        priority_weight = 0.0
        text_lower = input_text.lower()
        cand_lower = candidate_option.lower()

        if ("triage" in cand_lower or "pre-triage" in cand_lower) and any(t in text_lower for t in ["pain", "hurt", "ache", "swelling"]):
            priority_weight += 5.0
        if ("insurance" in cand_lower or "tpa" in cand_lower) and any(t in text_lower for t in ["claim", "card", "policy", "cashless"]):
            priority_weight += 5.0
        if ("book" in cand_lower or "slot" in cand_lower) and any(t in text_lower for t in ["time", "today", "tomorrow", "book"]):
            priority_weight += 5.0
        if ("branch" in cand_lower or "doctor" in cand_lower) and any(t in text_lower for t in ["where", "location", "who", "dr"]):
            priority_weight += 5.0

        return (overlap * 2.0) + priority_weight
