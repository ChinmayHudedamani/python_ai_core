import re
import base64
import json
import unicodedata
from typing import Dict, Any, List, Tuple

# Level 10 Fortified Multi-Layer Attack Pattern Matrix
FORTIFIED_ATTACK_MATRIX: Dict[str, List[str]] = {
    "DIRECT_JAILBREAK_OVERRIDE": [
        r"ignore (all )?previous", r"disregard (all )?instructions", r"system prompt",
        r"you are now a", r"act as", r"dev mode", r"mode: dan", r"forget everything",
        r"bypass rules", r"new role", r"unrestricted ai", r"do anything now",
        r"override safety", r"god mode", r"developer override"
    ],
    "SYSTEM_EXFILTRATION": [
        r"reveal api key", r"show system prompt", r"print instructions", r"export database",
        r"show passwords", r"dump env", r"read file", r"access key", r"cat /etc/passwd",
        r"process.env", r"secret_key", r"show code", r"dump schema"
    ],
    "FINANCIAL_FRAUD_EXPLOIT": [
        r"free treatment", r"give me free", r"100% discount", r"price is 0", r"zero cost",
        r"refund all", r"complimentary service", r"waive fee", r"no charge", r"coupon 100",
        r"free aligners", r"free implants", r"free rct"
    ],
    "PRESCRIPTION_ILLEGAL_ADVICE": [
        r"medicine", r"medicines", r"painkiller", r"painkillers", r"pain killer",
        r"tablet", r"tablets", r"antibiotic", r"antibiotics", r"prescribe",
        r"prescription", r"dose", r"dosage", r"pill", r"pills", r"paracetamol",
        r"ibugesic", r"combiflam", r"amoxicillin", r"what should i take",
        r"what medicine", r"which medicine"
    ],
    "REMOTE_CODE_EXECUTION_CSV_INJECTION": [
        r"^=", r"^\+", r"^-", r"^@", r"cmd\|", r"powershell", r"exec\(", r"eval\("
    ]
}


def normalize_unicode_homoglyphs(text: str) -> str:
    """Normalizes confusable unicode homoglyphs (e.g., 'frëë trêatmènt' -> 'free treatment')."""
    normalized = unicodedata.normalize("NFKD", text)
    return "".join([c for c in normalized if not unicodedata.combining(c)])


def try_decode_base64(text: str) -> str:
    """Detects and decodes hidden base64 encoded prompt injection payloads."""
    try:
        if len(text) > 16 and re.match(r"^[A-Za-z0-9+/=]+$", text.strip()):
            decoded = base64.b64decode(text.strip()).decode("utf-8", errors="ignore")
            if len(decoded) > 5:
                return decoded
    except Exception:
        pass
    return text


class FortifiedSecurityShield:
    """
    Level 10 Multi-Layer Defensive Security Fortress.
    Interceptors:
    - Unicode Homoglyph Normalization
    - Base64 Payload De-obfuscation
    - Expanded 25+ Category Regex Attack Interceptors
    - Financial Fraud & Zero-Price Exploit Deflector
    - Prescription Legal Refusal Shield
    """

    def inspect_input_security(self, raw_text: str) -> Dict[str, Any]:
        """Performs multi-layer security threat inspection."""
        if not raw_text or not isinstance(raw_text, str):
            return {"is_threat": False, "threat_categories": []}

        # 1. Unicode Normalization
        clean_text = normalize_unicode_homoglyphs(raw_text).lower()

        # 2. Base64 De-obfuscation
        decoded_text = try_decode_base64(clean_text)
        evaluated_text = f"{clean_text} {decoded_text.lower()}"

        threats_found: List[str] = []

        for category, patterns in FORTIFIED_ATTACK_MATRIX.items():
            if any(re.search(pat, evaluated_text) for pat in patterns):
                threats_found.append(category)

        # Obfuscated space character check (e.g. f r e e   t r e a t m e n t)
        deobfuscated_spaces: str = re.sub(r"\b(\w)\s+(\w)\s+(\w)\s+(\w)\b", r"\1\2\3\4", evaluated_text)
        if "free" in deobfuscated_spaces and "treatment" in deobfuscated_spaces and "FINANCIAL_FRAUD_EXPLOIT" not in threats_found:
            threats_found.append("FINANCIAL_FRAUD_EXPLOIT")

        return {
            "is_threat": len(threats_found) > 0,
            "threat_categories": threats_found,
            "normalized_text": clean_text
        }


if __name__ == "__main__":
    shield = FortifiedSecurityShield()
    test_attack = "frëë trêatmènt 100% discount"
    res = shield.inspect_input_security(test_attack)
    print(f"Attack Test: {test_attack}")
    print(json.dumps(res, indent=2))
