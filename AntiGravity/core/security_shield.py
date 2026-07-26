import re
from typing import Dict, Any, List

# Multi-Layer Enterprise Security Matrix
PROMPT_INJECTION_CATEGORIES: Dict[str, List[str]] = {
    "DIRECT_OVERRIDE": [
        r"ignore (all )?previous", r"disregard (all )?instructions", r"system prompt",
        r"you are now a", r"act as", r"dev mode", r"mode: dan", r"forget everything",
        r"bypass rules", r"new role"
    ],
    "FRAUD_EXPLOIT": [
        r"free treatment", r"give me free", r"100% discount", r"price is 0", r"zero cost",
        r"refund all", r"complimentary service", r"waive fee", r"no charge"
    ],
    "DATA_LEAK_ATTEMPT": [
        r"reveal api key", r"show system prompt", r"print instructions", r"export database",
        r"show passwords", r"dump env", r"read file", r"access key"
    ],
    "PRESCRIPTION_MEDICATION_ATTEMPT": [
        r"medicine", r"medicines", r"painkiller", r"painkillers", r"pain killer",
        r"tablet", r"tablets", r"antibiotic", r"antibiotics", r"prescribe",
        r"prescription", r"dose", r"dosage", r"pill", r"pills", r"paracetamol",
        r"ibugesic", r"combiflam", r"amoxicillin", r"what should i take",
        r"what medicine", r"which medicine"
    ]
}


def sanitize_user_input(text: str) -> str:
    """Strips control characters, prompt boundaries, and delimiter injections."""
    cleaned = re.sub(r"```|\[INST\]|<\|im_start\|>|<\|im_end\|>|system:", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", cleaned).strip()


def is_gibberish_text(text: str) -> bool:
    """Detects random keyboard spam or meaningless non-words."""
    text_clean = text.strip().lower()
    if len(text_clean) < 2:
        return False
    # Repeated characters like "asdfghjkl" or "aaaaa"
    if re.search(r"(.)\1{4,}", text_clean):
        return True
    return False


def inspect_security_threats(text: str) -> Dict[str, Any]:
    """Multi-layer Security Shield: Inspects direct overrides, financial fraud, data leaks, and prescription attempts."""
    text_clean: str = sanitize_user_input(text).lower()
    detected_threats: List[str] = []

    for category, patterns in PROMPT_INJECTION_CATEGORIES.items():
        for pattern in patterns:
            if re.search(pattern, text_clean):
                if category not in detected_threats:
                    detected_threats.append(category)

    return {
        "is_threat": len(detected_threats) > 0,
        "threat_count": len(detected_threats),
        "threat_categories": detected_threats,
        "sanitized_input": text_clean
    }
