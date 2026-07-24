import json
import re
from typing import Dict, Any, Tuple

HINGLISH_TRANSLATION_MAP: Dict[str, str] = {
    "daant": "tooth", "dant": "tooth", "teeths": "teeth", "dard": "pain",
    "dukh": "pain", "bohot": "severe", "bohut": "severe", "bahut": "severe",
    "jaldi": "urgent / ASAP", "kharcha": "cost / price", "kitna": "how much",
    "kitne": "how much", "dam": "price", "paisa": "cost", "paise": "cost",
    "rate": "price", "chahiye": "need / want", "khoon": "bleeding",
    "sojan": "swelling", "sujan": "swelling", "rct": "Root Canal",
    "implants": "Implants", "implant": "Implants", "aligners": "Aligners",
    "invisalign": "Invisalign Aligners"
}


def mask_pii(text: str) -> str:
    """Masks phone numbers and names for secure unencrypted logging."""
    return re.sub(r"(\+\d{2}|\d{3})\d{4,6}(\d{2})", r"\1****\2", text)


def validate_indian_phone_number(phone_str: str) -> Tuple[bool, str]:
    """
    Strict 10-Digit Indian Mobile Phone Validator.
    Valid Indian mobile numbers must be 10 digits starting with 6, 7, 8, or 9
    (optional +91 or leading 0 allowed).
    """
    if not isinstance(phone_str, str) or not phone_str.strip():
        return False, "Phone number cannot be empty."

    digits_only = re.sub(r"\D", "", phone_str)

    # Strip leading country code 91 or leading 0
    if len(digits_only) == 12 and digits_only.startswith("91"):
        digits_only = digits_only[2:]
    elif len(digits_only) == 11 and digits_only.startswith("0"):
        digits_only = digits_only[1:]

    if len(digits_only) != 10:
        return False, f"Invalid phone length ({len(digits_only)} digits). Indian mobile numbers must be exactly 10 digits."

    if not re.match(r"^[6-9]\d{9}$", digits_only):
        return False, "Invalid mobile prefix. Indian mobile numbers must start with 6, 7, 8, or 9."

    return True, f"+91-{digits_only[:5]}-{digits_only[5:]}"


def is_gibberish_text(text_str: str) -> bool:
    """
    Detects random keyboard mash / meaningless gibberish spam (e.g. 'ldQW;EKQDL/;l\'Wql;kkWJL;GEG').
    """
    if not text_str or len(text_str.strip()) < 3:
        return False

    clean_text = re.sub(r"[^\w\s]", "", text_str).strip()
    if not clean_text:
        return True

    words = clean_text.split()
    total_words = len(words)

    # 1. Check for long unbroken consonant clusters (> 5 consonants in a row)
    if re.search(r"[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]{6,}", clean_text):
        return True

    # 2. Check vowel ratio in alphabet characters
    letters = [c.lower() for c in clean_text if c.isalpha()]
    if letters:
        vowels = [c for c in letters if c in "aeiouy"]
        if len(letters) >= 8 and (len(vowels) / len(letters)) < 0.15:
            return True

    # 3. Check if words lack vowels
    nonsense_words = 0
    for w in words:
        if len(w) >= 5 and not any(v in w.lower() for v in "aeiouy"):
            nonsense_words += 1

    if total_words > 0 and (nonsense_words / total_words) >= 0.5:
        return True

    return False


def normalize_hinglish_text(text: str) -> str:
    """Translates Hinglish / regional keywords into clean English equivalents."""
    if not text:
        return ""
    words = text.split()
    translated_words = []
    for word in words:
        clean_word = re.sub(r"[^\w]", "", word).lower()
        translated_words.append(HINGLISH_TRANSLATION_MAP.get(clean_word, word))
    return " ".join(translated_words)


def clean_client_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitizes raw patient intake data and returns a cleaned dictionary."""
    if not isinstance(raw_data, dict):
        raw_data = {}

    cleaned_data: Dict[str, Any] = {}

    # 1. Clean Name
    name_val = raw_data.get("name")
    cleaned_data["name"] = name_val.strip().title() if isinstance(name_val, str) and name_val.strip() else "Unknown"

    # 2. Clean Phone
    phone_val = raw_data.get("phone")
    if isinstance(phone_val, str) and phone_val.strip():
        raw_phone = phone_val.strip()
        has_plus = raw_phone.startswith("+")
        digits_only = re.sub(r"\D", "", raw_phone)
        cleaned_data["phone"] = f"+{digits_only}" if has_plus else digits_only
    else:
        cleaned_data["phone"] = ""

    # 3. Clean Procedure Code
    code_val = raw_data.get("procedure_code")
    cleaned_data["procedure_code"] = code_val.strip().upper() if isinstance(code_val, str) and code_val.strip() else "N/A"

    # 4. Clean & Translate Notes
    notes_val = raw_data.get("notes")
    if isinstance(notes_val, str) and notes_val.strip():
        raw_notes = notes_val.strip()
        cleaned_data["raw_notes"] = raw_notes
        cleaned_data["notes"] = normalize_hinglish_text(raw_notes)
    else:
        cleaned_data["raw_notes"] = ""
        cleaned_data["notes"] = ""

    return cleaned_data


def format_to_json(cleaned_data: Dict[str, Any]) -> str:
    """Converts a dictionary into a formatted JSON payload."""
    return json.dumps(cleaned_data, indent=2)


if __name__ == "__main__":
    messy_patient_input = {
        "name": "   chinmay hudedamani  ",
        "phone": "+91-9876543210",
        "procedure_code": "  rct-01 ",
        "notes": "  Experiencing severe pain in lower right molar.  "
    }

    cleaned_dict = clean_client_data(messy_patient_input)
    print("--- SANITIZED PATIENT PAYLOAD ---")
    print(format_to_json(cleaned_dict))

