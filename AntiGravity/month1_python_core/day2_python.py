import json
import re

# Hinglish / Regional to English translation map for Intake Normalization
HINGLISH_TRANSLATION_MAP = {
    "daant": "tooth",
    "dant": "tooth",
    "teeths": "teeth",
    "dard": "pain",
    "dukh": "pain",
    "bohot": "severe",
    "bohut": "severe",
    "bahut": "severe",
    "jaldi": "urgent / ASAP",
    "kharcha": "cost / price",
    "kitna": "how much",
    "kitne": "how much",
    "dam": "price",
    "paisa": "cost",
    "paise": "cost",
    "rate": "price",
    "chahiye": "need / want",
    "khoon": "bleeding",
    "sojan": "swelling",
    "sujan": "swelling",
    "rct": "Root Canal",
    "implants": "Implants",
    "implant": "Implants",
    "aligners": "Aligners",
    "invisalign": "Invisalign Aligners"
}


def normalize_hinglish_text(text: str) -> str:
    """
    Translates Hinglish / regional keywords into clean English equivalents.
    """
    words = text.split()
    translated_words = []
    for word in words:
        # Strip punctuation for dictionary lookup
        clean_word = re.sub(r"[^\w]", "", word).lower()
        if clean_word in HINGLISH_TRANSLATION_MAP:
            translated_words.append(HINGLISH_TRANSLATION_MAP[clean_word])
        else:
            translated_words.append(word)
    return " ".join(translated_words)


def clean_client_data(raw_data: dict) -> dict:
    """
    Sanitizes raw patient intake data and returns a cleaned dictionary.
    - Strips leading/trailing whitespace
    - Formats patient name to Proper Case (.title())
    - Cleans phone numbers (removes spaces, dashes, parentheses)
    - Uppercases procedure codes (.upper())
    - Translates & normalizes Hinglish/regional notes to English
    """
    cleaned_data = {}
    
    # 1. Clean Name (strip whitespace, title case)
    if "name" in raw_data and isinstance(raw_data["name"], str):
        cleaned_data["name"] = raw_data["name"].strip().title()
    else:
        cleaned_data["name"] = "Unknown"

    # 2. Clean Phone (strip whitespace, remove dashes/spaces/parentheses)
    if "phone" in raw_data and isinstance(raw_data["phone"], str):
        raw_phone = raw_data["phone"].strip()
        has_plus = raw_phone.startswith("+")
        digits_only = re.sub(r"\D", "", raw_phone)
        cleaned_data["phone"] = f"+{digits_only}" if has_plus else digits_only
    else:
        cleaned_data["phone"] = ""

    # 3. Clean Procedure Code (strip whitespace, uppercase)
    if "procedure_code" in raw_data and isinstance(raw_data["procedure_code"], str):
        cleaned_data["procedure_code"] = raw_data["procedure_code"].strip().upper()
    else:
        cleaned_data["procedure_code"] = "N/A"

    # 4. Clean & Translate Notes / Inquiry text (Hinglish -> English translation)
    if "notes" in raw_data and isinstance(raw_data["notes"], str):
        raw_notes = raw_data["notes"].strip()
        cleaned_data["raw_notes"] = raw_notes
        cleaned_data["notes"] = normalize_hinglish_text(raw_notes)
    else:
        cleaned_data["raw_notes"] = ""
        cleaned_data["notes"] = ""

    return cleaned_data


def format_to_json(cleaned_data: dict) -> str:
    """Converts a dictionary into a formatted JSON payload."""
    return json.dumps(cleaned_data, indent=2)


if __name__ == "__main__":
    # Test with messy input data
    messy_patient_input = {
        "name": "   chinmay hudedamani  ",
        "phone": " +91-98765 XXX70 ",
        "procedure_code": "  rct-01 ",
        "notes": "  Experiencing severe pain in lower right molar.  "
    }

    print("--- RAW MESSY INPUT ---")
    print(messy_patient_input)
    print("\n--- CLEANING DATA ---")
    cleaned_dict = clean_client_data(messy_patient_input)
    print(cleaned_dict)

    print("\n--- FORMATTED JSON PAYLOAD ---")
    json_payload = format_to_json(cleaned_dict)
    print(json_payload)
