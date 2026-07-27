# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Universal Short-Text & Micro-Input Context Augmentation Normalizer

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("APEX_AI_NORMALIZERS")

AFFIRMATIVE_WORDS = {"yes", "sure", "okay", "ok", "yep", "yeah", "haan", "chalega", "confirm", "done", "book"}
PRICING_WORDS = {"price", "pricing", "cost", "how much", "rate", "fees"}
SIDE_INQUIRY_WORDS = {"tablet", "tablets", "medicine", "medication", "painkiller", "direction", "location", "address", "parking"}


def augment_short_text(user_text: str, session_state: Dict[str, str]) -> Dict[str, Any]:
    """Inspects short-text/single-word inputs (<= 3 words) and augments them using active session state context."""
    if not user_text:
        return {"was_augmented": False, "original_text": "", "augmented_text": ""}

    raw_text = user_text.strip()
    words = raw_text.split()

    if len(words) > 3:
        return {"was_augmented": False, "original_text": raw_text, "augmented_text": raw_text}

    lower_text = raw_text.lower().replace("?", "").strip()

    # If input contains a side inquiry (tablets, directions, parking), pass through without slot interception
    if any(w in lower_text for w in SIDE_INQUIRY_WORDS):
        return {"was_augmented": False, "original_text": raw_text, "augmented_text": raw_text}

    last_intent = session_state.get("last_intent", session_state.get("pinned_current_intent", "GENERAL_INQUIRY"))
    last_topic = session_state.get("last_topic", "General Consultation")

    augmented = raw_text
    applied_rule = None

    # Rule 1: Affirmative confirmations when selecting slot or confirming code
    if lower_text in AFFIRMATIVE_WORDS:
        if last_intent in ["SELECTING_SLOT", "SLOT_BOOKING"]:
            augmented = "Yes, confirm the pending appointment slot."
            applied_rule = "AFFIRMATIVE_SLOT_CONFIRMATION"
        elif last_intent == "CONFIRMING_CODE" or session_state.get("pending_code"):
            code = session_state.get("pending_code", "APX-4928")
            augmented = f"Yes, confirm my appointment with check-in code {code}."
            applied_rule = "AFFIRMATIVE_CODE_CONFIRMATION"

    # Rule 2: Short pricing queries (e.g. "Price?", "How much?", "Implants")
    elif any(w in lower_text for w in PRICING_WORDS) or lower_text in ["implants", "rct", "aligners", "invisalign"]:
        topic = "Implants" if "implant" in lower_text else ("Root Canal" if "rct" in lower_text else last_topic)
        augmented = f"What is the total price and cost breakdown of {topic} treatment?"
        applied_rule = "SHORT_PRICING_EXPANSION"

    # Rule 3: Doctor name shorthand (e.g. "Nair", "Sharma")
    elif lower_text in ["nair", "dr nair", "dr nair's", "sharma", "dr sharma"]:
        doc_name = "Dr. Rajesh Nair" if "nair" in lower_text else "Dr. Vikram Sharma"
        augmented = f"Check available appointment slots for {doc_name}."
        applied_rule = "DOCTOR_NAME_EXPANSION"

    # Rule 4: Date shorthand (e.g. "Tomorrow", "Today", "Saturday")
    elif lower_text in ["tomorrow", "today", "saturday", "monday"]:
        augmented = f"Check available consultation slots for {raw_text}."
        applied_rule = "DATE_SHORTHAND_EXPANSION"

    if augmented != raw_text:
        logger.info(f"💡 Short-Text Context Injection ({applied_rule}): '{raw_text}' -> '{augmented}'")
        return {
            "was_augmented": True,
            "original_text": raw_text,
            "augmented_text": augmented,
            "applied_rule": applied_rule
        }

    return {"was_augmented": False, "original_text": raw_text, "augmented_text": raw_text}
