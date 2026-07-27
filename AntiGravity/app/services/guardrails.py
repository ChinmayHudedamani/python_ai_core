# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Enterprise Pre/Post Guardrail Pipeline & Circuit Breaker

import re
import functools
import asyncio
from typing import Dict, Any, Callable


PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"system\s+prompt",
    r"you\s+are\s+now\s+a",
    r"bypass\s+(security|guardrails|safety)",
    r"override\s+rules",
    r"act\s+as\s+an?\s+unrestricted",
    r"disregard\s+all\s+rules",
    r"forget\s+your\s+role",
]


def sanitize_input(text: str) -> Dict[str, Any]:
    """Inspects input for prompt injection attack patterns and returns XML-sandboxed text."""
    if not text:
        return {"is_flagged": False, "sanitized_text": "<user_input></user_input>"}

    raw_text = text.strip()

    # Regex inspection for prompt injection phrases
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, raw_text, flags=re.IGNORECASE):
            return {
                "is_flagged": True,
                "flag_reason": f"Prompt injection pattern detected: '{pattern}'",
                "sanitized_text": f"<user_input_flagged>{raw_text}</user_input_flagged>"
            }

    # XML Sandboxing to prevent context confusion
    sandboxed_text = f"<user_input>{raw_text}</user_input>"
    return {
        "is_flagged": False,
        "flag_reason": None,
        "sanitized_text": sandboxed_text
    }


def with_circuit_breaker(timeout: float = 4.0):
    """Decorator yielding 4.0s timeout circuit breaker with deterministic fallback & HITL handoff."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except asyncio.TimeoutError:
                return {
                    "is_circuit_broken": True,
                    "response_text": (
                        "I am experiencing a slight delay. Let me connect you to our front desk "
                        "receptionist who can assist you right away!"
                    ),
                    "trigger_hitl": True,
                    "confidence_score": 0.0,
                    "user_sentiment": "URGENT"
                }
        return wrapper
    return decorator
