import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from typing import Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from day6_python import SafetyCircuitBreaker
from twilio_dispatcher import TwilioWhatsAppDispatcher
from twilio_config import load_twilio_credentials

PORT: int = 5000
breaker = SafetyCircuitBreaker()
dispatcher = TwilioWhatsAppDispatcher()


class TwilioWhatsAppWebhookHandler(BaseHTTPRequestHandler):
    """
    HTTP Webhook Handler for Twilio WhatsApp Sandbox.
    Receives incoming WhatsApp texts from patients, processes through Centaur OS RAG engine,
    and returns real-time TwiML XML or outbound WhatsApp message dispatches.
    """

    def do_POST(self):
        """Processes incoming POST webhook from Twilio."""
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)
        body_str = body_bytes.decode("utf-8")

        # Parse urlencoded Form Data from Twilio
        params = parse_qs(body_str)

        raw_from = params.get("From", [""])[0]  # e.g. "whatsapp:+919988776655"
        text_body = params.get("Body", [""])[0]
        profile_name = params.get("ProfileName", ["Patient"])[0]

        clean_phone = raw_from.replace("whatsapp:", "").strip()

        print(f"\n📩 [TWILIO INCOMING WHATSAPP]: From={profile_name} ({clean_phone})")
        print(f"   Message: \"{text_body}\"")

        raw_intake = {
            "name": profile_name,
            "phone": clean_phone,
            "procedure_code": "GENERAL",
            "notes": text_body
        }

        # Process through Centaur OS Safety Circuit & RAG Generator
        result = breaker.process_intake_safety_circuit(raw_intake)
        reply_text = result.get("whatsapp_response", "")

        # Format TwiML Messaging Response XML for Twilio
        twiml_xml = (
            f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            f"<Response>\n"
            f"    <Message>{reply_text}</Message>\n"
            f"</Response>"
        )

        self.send_response(200)
        self.send_header("Content-Type", "application/xml; charset=utf-8")
        self.end_headers()
        self.wfile.write(twiml_xml.encode("utf-8"))

        print(f"  ⚡ [TWILIO DISPATCH SENT] Sent TwiML reply to {clean_phone}")


def start_twilio_webhook_server():
    server = HTTPServer(("0.0.0.0", PORT), TwilioWhatsAppWebhookHandler)
    creds = load_twilio_credentials()
    sandbox_num = creds.get("sandbox_whatsapp_number", "whatsapp:+14155238886")

    print("\n==================================================")
    print(" 📱 CENTAUR CLINIC TWILIO WHATSAPP SANDBOX SERVER")
    print("==================================================")
    print(f" 🌐 Webhook Listening on: http://localhost:{PORT}/twilio/webhook")
    print(f" 📲 Twilio Sandbox Number: {sandbox_num}")
    print("\n📋 EASY 3-STEP TWILIO LIVE DEMO SETUP:")
    print(" 1. Open WhatsApp on your phone and send 'join <sandbox-code>' to +1 415 523 8886")
    print(f" 2. Run ngrok in command prompt: ngrok http {PORT}")
    print(" 3. Paste the ngrok URL into Twilio Sandbox Webhook Settings!")
    print("==================================================\n")
    server.serve_forever()


if __name__ == "__main__":
    start_twilio_webhook_server()
