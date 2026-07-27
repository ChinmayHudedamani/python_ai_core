"""Pre- and post-execution guardrails, prompt injection sanitization, and circuit breakers."""

import re
import functools
import asyncio
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger("APEX_AI_GUARDRAILS")

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"you\s+are\n+now",
    r"system\s+prompt",
    r"jailbreak",
    r"override\s+rules",
    r"act\s+as\s+a"
]


def sanitize_input(user_text: str) -> Dict[str, Any]:
    """Sanitizes user input, detecting prompt injection patterns and sandboxing within XML tags."""
    if not user_text:
        return {"is_flagged": False, "sanitized_text": "", "flag_reason": None}

    raw_text = user_text.strip()

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, raw_text, re.IGNORECASE):
            logger.warning(f"🚨 Prompt Injection Attack Detected: Pattern '{pattern}' in text: '{raw_text}'")
            return {
                "is_flagged": True,
                "sanitized_text": raw_text,
                "flag_reason": f"Prompt injection pattern detected: '{pattern}'"
            }

    sandboxed_text = f"<user_input>{raw_text}</user_input>"
    return {
        "is_flagged": False,
        "sanitized_text": sandboxed_text,
        "flag_reason": None
    }


def with_circuit_breaker(timeout: float = 4.0):
    """Decorator wrapping async functions with a hard time-limit fallback."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except asyncio.TimeoutError:
                logger.error(f"🚨 Circuit Breaker Triggered: Function '{func.__name__}' timed out (> {timeout}s)")
                return "I am experiencing a slight delay. Let me connect you to our front desk receptionist who can assist you right away!"
        return wrapper
    return decorator
