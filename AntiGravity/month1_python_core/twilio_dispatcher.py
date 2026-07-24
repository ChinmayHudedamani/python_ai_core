import json
import sys
import base64
import urllib.request
import urllib.parse
from typing import Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from twilio_config import load_twilio_credentials


class TwilioWhatsAppDispatcher:
    """
    Twilio Free WhatsApp Sandbox Message Dispatcher.
    Sends real-time WhatsApp text messages to patient and doctor phones using standard urllib.
    """

    def __init__(self):
        self.creds = load_twilio_credentials()
        self.account_sid = self.creds.get("account_sid", "")
        self.auth_token = self.creds.get("auth_token", "")
        self.from_number = self.creds.get("sandbox_whatsapp_number", "whatsapp:+14155238886")

    def send_whatsapp_message(self, to_phone: str, message_body: str) -> Dict[str, Any]:
        """
        Sends an outbound WhatsApp text message to a patient/doctor mobile number via Twilio REST API.
        """
        clean_to = to_phone.strip().replace(" ", "").replace("-", "")
        if not clean_to.startswith("whatsapp:"):
            clean_to = f"whatsapp:{clean_to}"

        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"

        data = urllib.parse.urlencode({
            "From": self.from_number,
            "To": clean_to,
            "Body": message_body
        }).encode("utf-8")

        auth_str = f"{self.account_sid}:{self.auth_token}"
        b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Authorization", f"Basic {b64_auth}")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        try:
            with urllib.request.urlopen(req) as response:
                resp_body = response.read().decode("utf-8")
                resp_data = json.loads(resp_body)
                print(f"  ✅ [TWILIO SUCCESS] Sent WhatsApp to {clean_to} (SID: {resp_data.get('sid')})")
                return {"status": "DISPATCH_SUCCESS", "sid": resp_data.get("sid"), "to": clean_to}
        except Exception as e:
            print(f"  ⚠️ [TWILIO SIMULATED DISPATCH] ({clean_to}): {e}")
            return {
                "status": "SIMULATED_DISPATCH",
                "to": clean_to,
                "message": message_body,
                "note": "Provide valid Twilio Account SID & Auth Token in twilio_credentials.json to send real live WhatsApp messages!"
            }


if __name__ == "__main__":
    dispatcher = TwilioWhatsAppDispatcher()
    res = dispatcher.send_whatsapp_message("+919988776655", "Hello from Centaur OS WhatsApp Engine!")
    print(json.dumps(res, indent=2))
