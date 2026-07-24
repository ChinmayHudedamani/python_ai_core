import json
import hmac
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from typing import Dict, Any

from whatsapp_dispatcher import EliteWhatsAppChannelDispatcher
from hardened_security_shield import FortifiedSecurityShield
from day6_python import SafetyCircuitBreaker

META_VERIFY_TOKEN: str = "apex_centaur_meta_verify_token_2026"
META_APP_SECRET: str = "apex_dental_centaur_secret_key_2026"
PORT: int = 8080

dispatcher = EliteWhatsAppChannelDispatcher()
security = FortifiedSecurityShield()
circuit = SafetyCircuitBreaker()


class MetaWhatsAppWebhookHandler(BaseHTTPRequestHandler):
    """
    Production Meta WhatsApp Business API Cloud Webhook HTTP Handler.
    Handles GET webhook verification (Meta setup) and POST message dispatches.
    """

    def do_GET(self):
        """Meta Webhook Challenge Verification Handler."""
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)

        mode = params.get("hub.mode", [""])[0]
        token = params.get("hub.verify_token", [""])[0]
        challenge = params.get("hub.challenge", [""])[0]

        if mode == "subscribe" and token == META_VERIFY_TOKEN:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(challenge.encode("utf-8"))
            print("  ✅ [WEBHOOK] Meta WhatsApp Webhook Challenge Verification Succeeded!")
        else:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Forbidden: Verification Token Mismatch.")

    def do_POST(self):
        """Incoming WhatsApp Patient Message Receiver & Automated Dispatcher."""
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)
        body_str = body_bytes.decode("utf-8")

        # Signature Validation
        signature_header = self.headers.get("X-Hub-Signature-256", "")
        expected_sig = hmac.new(META_APP_SECRET.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()

        if signature_header and not hmac.compare_digest(signature_header, f"sha256={expected_sig}"):
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b"Unauthorized: HMAC Signature Mismatch.")
            return

        try:
            payload = json.loads(body_str)
            print("\n📩 [PRODUCTION WEBHOOK INCOMING PAYLOAD]:")
            print(json.dumps(payload, indent=2))

            # Extract message details
            entry = payload.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])

            if messages:
                msg = messages[0]
                from_phone = msg.get("from", "")
                text_body = msg.get("text", {}).get("body", "")
                contact_name = value.get("contacts", [{}])[0].get("profile", {}).get("name", "Patient")

                raw_intake = {
                    "name": contact_name,
                    "phone": f"+{from_phone}",
                    "procedure_code": "GENERAL",
                    "notes": text_body
                }

                # Process through safety circuit & RAG pipeline
                dispatch_res = dispatcher.process_and_dispatch_elite(raw_intake)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(dispatch_res).encode("utf-8"))
                return
        except Exception as e:
            print(f"⚠️ Error processing webhook: {e}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "EVENT_RECEIVED"}')


def start_production_webhook_server():
    server = HTTPServer(("0.0.0.0", PORT), MetaWhatsAppWebhookHandler)
    print(f"\n==================================================")
    print(f" 🚀 PRODUCTION META WHATSAPP WEBHOOK SERVER RUNNING")
    print(f" 🌐 Listening on: http://0.0.0.0:{PORT}/webhook")
    print(f" 🔑 Verification Token: {META_VERIFY_TOKEN}")
    print(f"==================================================\n")
    server.serve_forever()


if __name__ == "__main__":
    start_production_webhook_server()
