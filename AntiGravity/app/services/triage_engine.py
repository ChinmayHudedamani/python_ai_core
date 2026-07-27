# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Multilingual Zero-Latency Emergency Triage Engine

import re
from typing import Dict, Any, Optional
from sqlmodel import select
from app.core.sqlite_db import get_sqlite_session
from app.models.kb import ClinicalTriageRule


class TriageEngine:
    """Zero-latency Multilingual Emergency Triage Engine."""

    def __init__(self):
        pass

    def _normalize_text(self, text: str) -> str:
        """Normalizes text while preserving Devanagari script (U+0900 to U+097F)."""
        text_lower = text.lower()
        # Preserve alphanumeric, whitespace, and Devanagari script
        cleaned = re.sub(r"[^\w\s\u0900-\u097F]", " ", text_lower)
        return " ".join(cleaned.split())

    def evaluate_message(self, message: str) -> Optional[Dict[str, Any]]:
        """Evaluates patient message against triage rules stored in SQLite."""
        if not message or not message.strip():
            return None

        normalized_msg = self._normalize_text(message)

        with get_sqlite_session() as session:
            rules = session.exec(select(ClinicalTriageRule)).all()
            for rule in rules:
                keyword = rule.symptom_keyword.lower().strip()
                if not keyword:
                    continue

                # Regex word-boundary match
                # For Devanagari or non-ASCII, use custom boundary check if needed
                pattern = r"(?:^|\s)" + re.escape(keyword) + r"(?:$|\s)" if any(ord(c) > 127 for c in keyword) else r"\b" + re.escape(keyword) + r"\b"

                if re.search(pattern, normalized_msg, flags=re.IGNORECASE) or keyword in normalized_msg:
                    return {
                        "urgency_level": rule.urgency_level,
                        "matched_keyword": rule.symptom_keyword,
                        "first_aid_instructions": rule.first_aid_instructions
                    }

        return None
