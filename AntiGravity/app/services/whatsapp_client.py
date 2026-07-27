"""Async HTTPX Client for Meta WhatsApp Cloud API outbound egress messaging."""

import logging
import httpx
from typing import Dict, Any, Optional

from app.core.config import settings

logger = logging.getLogger("APEX_AI_WHATSAPP_CLIENT")


class WhatsAppClient:
    """Outbound client for dispatching WhatsApp messages via Graph API."""

    def __init__(self):
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def send_text_message(self, to_phone: str, message: str) -> Dict[str, Any]:
        """Dispatches text message to recipient."""
        clean_phone = to_phone.replace("+", "").replace("-", "").strip()
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone,
            "type": "text",
            "text": {"preview_url": False, "body": message}
        }

        if self.access_token == "default_access_token":
            logger.info(f"📱 [SIMULATION OUTBOUND WHATSAPP] To: {clean_phone} | Msg: {message}")
            return {"messaging_product": "whatsapp", "contacts": [{"input": clean_phone}], "messages": [{"id": "wamid.simulated"}]}

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(self.base_url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Failed to dispatch WhatsApp message to {clean_phone}: {e}")
                return {"error": str(e)}
