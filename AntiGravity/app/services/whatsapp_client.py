# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Meta Official WhatsApp Cloud API Egress Client

import os
import logging
import httpx
from typing import Dict, Any, List, Optional

logger = logging.getLogger("APEX_AI_WHATSAPP_CLIENT")

WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "mock_access_token_12345")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "mock_phone_number_id_67890")
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v18.0")


class WhatsAppClient:
    """Outbound Egress Client for Meta WhatsApp Cloud API."""

    def __init__(self, access_token: Optional[str] = None, phone_number_id: Optional[str] = None):
        self.access_token = access_token or WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = phone_number_id or WHATSAPP_PHONE_NUMBER_ID
        self.base_url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{self.phone_number_id}/messages"

    def _format_recipient_phone(self, phone: str) -> str:
        """Formats recipient phone to digits only (e.g. 917338350871)."""
        clean = phone.replace("+", "").replace("-", "").replace(" ", "").strip()
        return clean

    async def send_text_message(self, to_phone: str, message: str) -> Dict[str, Any]:
        """Dispatches outbound text message to patient via Meta Cloud API."""
        recipient = self._format_recipient_phone(to_phone)
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }

        logger.info(f"📤 Dispatching WhatsApp Message to {recipient} ({len(message)} chars)")

        # In mock / test mode without live token, log payload cleanly
        if self.access_token.startswith("mock_"):
            logger.info(f"ℹ️ [MOCK WHATSAPP EGRESS DISPATCH]: To: {recipient} | Message: '{message}'")
            return {
                "messaging_product": "whatsapp",
                "contacts": [{"input": recipient, "wa_id": recipient}],
                "messages": [{"id": f"wamid.mock_{recipient}"}],
                "is_mock": True
            }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                res_data = response.json()
                logger.info(f"✅ Meta WhatsApp Egress Success: {res_data}")
                return res_data
            except Exception as e:
                logger.error(f"❌ Meta WhatsApp Egress Failed for {recipient}: {e}")
                return {"error": str(e), "is_mock": False}

    async def send_template_message(
        self,
        to_phone: str,
        template_name: str,
        components: Optional[List[Dict[str, Any]]] = None,
        language_code: str = "en_US"
    ) -> Dict[str, Any]:
        """Dispatches Meta WhatsApp Template message for 24-hour reminders."""
        recipient = self._format_recipient_phone(to_phone)
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                "components": components or []
            }
        }

        logger.info(f"📤 Dispatching WhatsApp Template '{template_name}' to {recipient}")

        if self.access_token.startswith("mock_"):
            logger.info(f"ℹ️ [MOCK WHATSAPP TEMPLATE DISPATCH]: To: {recipient} | Template: '{template_name}'")
            return {
                "messaging_product": "whatsapp",
                "contacts": [{"input": recipient, "wa_id": recipient}],
                "messages": [{"id": f"wamid.mock_template_{recipient}"}],
                "is_mock": True
            }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"❌ Meta WhatsApp Template Dispatch Failed for {recipient}: {e}")
                return {"error": str(e), "is_mock": False}
