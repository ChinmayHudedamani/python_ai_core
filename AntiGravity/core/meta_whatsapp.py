import os
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MetaWhatsAppCloudEngine:
    """Official Meta WhatsApp Cloud API Integration Engine (Direct Meta Graph API)."""

    def __init__(self):
        self.access_token = os.getenv("META_WA_ACCESS_TOKEN", "")
        self.phone_number_id = os.getenv("META_WA_PHONE_NUMBER_ID", "")
        self.verify_token = os.getenv("META_WA_VERIFY_TOKEN", "centaur_meta_secret_2026")
        self.graph_url = f"https://graph.facebook.com/v19.0/{self.phone_number_id}/messages"

    def send_whatsapp_message(self, recipient_phone: str, message_body: str) -> Dict[str, Any]:
        """Dispatches outbound WhatsApp text message directly via Meta Graph API."""
        clean_phone = recipient_phone.replace("+", "").replace("-", "").replace(" ", "").replace("whatsapp:", "").strip()

        if not self.access_token or not self.phone_number_id:
            logger.warning("Meta WhatsApp Cloud API credentials (META_WA_ACCESS_TOKEN / META_WA_PHONE_NUMBER_ID) missing.")
            return {
                "status": "SIMULATED_META_DISPATCH",
                "to": clean_phone,
                "body": message_body,
                "message": "Meta credentials missing in environment variables"
            }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone,
            "type": "text",
            "text": {
                "preview_url": True,
                "body": message_body
            }
        }

        try:
            # Enforce (connect, read) timeout tuple to prevent Gunicorn worker freezing
            response = requests.post(self.graph_url, json=payload, headers=headers, timeout=(3.05, 5.0))
            res_data = response.json()
            if response.status_code == 200 and "messages" in res_data:
                msg_id = res_data["messages"][0]["id"]
                logger.info(f"✅ [META WHATSAPP SUCCESS] Sent to {clean_phone} (ID: {msg_id})")
                return {"status": "DISPATCH_SUCCESS", "message_id": msg_id, "to": clean_phone}
            else:
                logger.error(f"🚨 [META WHATSAPP ERROR]: {res_data}")
                return {"status": "DISPATCH_FAILED", "error": res_data}
        except Exception as ex:
            logger.error(f"🚨 [META DISPATCH EXCEPTION]: {ex}")
            return {"status": "EXCEPTION", "error": str(ex)}
