# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# Official Gemini MIDGO Structured Output Client Wrapper

import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.core.config import settings
from app.services.schemas import MIDGODentalResponse

load_dotenv()
logger = logging.getLogger("APEX_AI_MIDGO_CLIENT")


class GeminiMIDGOClient:
    """Official SDK Structured Output Handler for Gemini 2.5 Flash MIDGO Architecture."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("DEFAULT_LLM_MODEL") or settings.DEFAULT_LLM_MODEL or "gemini-2.5-flash"

    def process_turn(self, system_prompt: str, user_message: str) -> MIDGODentalResponse:
        """Executes structured JSON content generation enforcing MIDGODentalResponse Pydantic schema."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=MIDGODentalResponse,
                    temperature=0.3,
                ),
            )
            return MIDGODentalResponse.model_validate_json(response.text)
        except Exception as e:
            logger.error(f"MIDGO turn processing error: {e}")
            return MIDGODentalResponse(
                extracted_name="",
                extracted_symptom_or_reason="",
                classified_intent="FAQ_INQUIRY",
                patient_reply="I understand! Let me connect you to our front desk receptionist at Apex Dental Koramangala who can assist you right away!"
            )


# Class alias for backward compatibility
GeminiClientWrapper = GeminiMIDGOClient
