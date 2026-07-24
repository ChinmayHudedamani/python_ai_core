import unittest
import json
from flask_backend_server import app, processed_sids


class TestFlaskEnterpriseBackend(unittest.TestCase):
    """Rigorous Unit Test Suite for Flask Enterprise Backend."""

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_01_health_check_endpoint(self):
        """Verifies GET / health check endpoint."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "HEALTHY")
        self.assertIn("uptime_seconds", data)
        print("  ✅ [PASS 1/5] GET / Health Check Endpoint Verified.")

    def test_02_whatsapp_webhook_twi_ml(self):
        """Verifies POST /webhook/whatsapp returns TwiML XML payload."""
        response = self.app.post('/webhook/whatsapp', data={
            "MessageSid": "SM_TEST_FLASK_001",
            "From": "whatsapp:+919876543210",
            "Body": "What is the cost of clear aligners in Koramangala?",
            "ProfileName": "Ananya Roy"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/xml", response.content_type)
        self.assertIn("<?xml version=", response.data.decode("utf-8"))
        self.assertIn("Apex Dental Center", response.data.decode("utf-8"))
        print("  ✅ [PASS 2/5] POST /webhook/whatsapp TwiML XML Response Verified.")

    def test_03_atomic_sid_deduplication(self):
        """Verifies duplicate MessageSid is deduplicated with empty response."""
        response = self.app.post('/webhook/whatsapp', data={
            "MessageSid": "SM_TEST_FLASK_001",  # Duplicate SID
            "From": "whatsapp:+919876543210",
            "Body": "What is the cost of clear aligners in Koramangala?",
            "ProfileName": "Ananya Roy"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode("utf-8"), '<?xml version="1.0" encoding="UTF-8"?><Response></Response>')
        print("  ✅ [PASS 3/5] Atomic SID Deduplication Hold Verified.")

    def test_04_patient_intake_rest_api(self):
        """Verifies POST /api/v1/intake REST API endpoint."""
        response = self.app.post('/api/v1/intake', json={
            "notes": "Hi, I need an appointment for Saturday at 11 AM.",
            "name": "Rohan Sharma",
            "phone": "+919111222333"
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "PROCESSED_SUCCESSFULLY")
        self.assertIn("whatsapp_response", data)
        print("  ✅ [PASS 4/5] POST /api/v1/intake REST API Endpoint Verified.")

    def test_05_telemetry_api_endpoint(self):
        """Verifies GET /api/v1/telemetry analytics endpoint."""
        response = self.app.get('/api/v1/telemetry')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("telemetry", data)
        print("  ✅ [PASS 5/5] GET /api/v1/telemetry Analytics Endpoint Verified.")


if __name__ == "__main__":
    print("\n==================================================")
    print(" 🧪 TESTING CENTAUR OS FLASK ENTERPRISE BACKEND")
    print("==================================================")
    unittest.main()
