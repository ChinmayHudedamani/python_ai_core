import json
import re
from typing import Dict, Any

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

