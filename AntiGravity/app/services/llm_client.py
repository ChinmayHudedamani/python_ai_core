"""Official Google GenAI Client Wrapper for Gemini 2.5 Flash / Pro Integration."""

import os
import logging
from typing import Optional, List, Any
from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger("APEX_AI_GEMINI_CLIENT")


class GeminiClientWrapper:
    """Official SDK Wrapper for Google GenAI Models."""

    def __init__(self):
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model = settings.DEFAULT_LLM_MODEL or "gemini-2.5-flash"

    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        tools: Optional[List[Any]] = None
    ) -> str:
        """Generates async response using Google GenAI SDK."""
        config_params = {
            "system_instruction": system_prompt,
            "temperature": 0.3,
        }
        if tools:
            config_params["tools"] = tools

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=user_message,
                config=types.GenerateContentConfig(**config_params)
            )
            return response.text or ""
        except Exception as e:
            logger.error(f"Gemini API generation error: {e}")
            return "I am experiencing a slight delay. Let me connect you to our front desk receptionist who can assist you right away!"
