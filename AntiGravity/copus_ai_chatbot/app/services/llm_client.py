# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# Official Gemini MIDGO Structured Output Client Wrapper & Telemetry Audit Logger

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.core.config import settings
from app.services.schemas import MIDGODentalResponse, TAXONOMY_30_INTENTS

load_dotenv()
logger = logging.getLogger("APEX_AI_MIDGO_CLIENT")

# Telemetry Log Directory Initialization
LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
TELEMETRY_LOG_PATH = LOGS_DIR / "telemetry.jsonl"


def log_telemetry_event(event_type: str, payload: dict):
    """Appends an interaction or audit event to logs/telemetry.jsonl."""
    try:
        record = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "payload": payload
        }
        with open(TELEMETRY_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as e:
        logger.error(f"Failed to log telemetry event: {e}")


class GeminiMIDGOClient:
    """Official SDK Structured Output Handler for Gemini 2.5 Flash MIDGO Architecture."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("DEFAULT_LLM_MODEL") or getattr(settings, "DEFAULT_LLM_MODEL", "gemini-2.5-flash")

    def process_turn(self, system_prompt: str, user_message: str) -> MIDGODentalResponse:
        """Executes structured JSON generation enforcing MIDGODentalResponse schema."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=MIDGODentalResponse,
                    temperature=0.2,
                ),
            )
            parsed: MIDGODentalResponse = MIDGODentalResponse.model_validate_json(response.text)
            
            # Log successful turn telemetry
            log_telemetry_event("LLM_TURN_SUCCESS", {
                "user_message": user_message,
                "classified_intent": parsed.classified_intent,
                "extracted_name": parsed.extracted_name,
                "extracted_symptom": parsed.extracted_symptom_or_reason
            })
            return parsed

        except Exception as e:
            logger.error(f"MIDGO turn processing error: {e}")
            fallback = MIDGODentalResponse(
                extracted_name="",
                extracted_symptom_or_reason="",
                classified_intent="INTENT_CONSULT_FEE",
                patient_reply="I understand! Let me connect you to our front desk receptionist at Apex Dental Yelahanka Node who can assist you right away!"
            )
            # Log turn failure telemetry
            log_telemetry_event("LLM_TURN_EXCEPTION", {
                "user_message": user_message,
                "error": str(e)
            })
            return fallback


# Backward Compatibility Alias
GeminiClientWrapper = GeminiMIDGOClient
