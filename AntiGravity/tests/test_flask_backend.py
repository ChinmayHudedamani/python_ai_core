import os
import sys
import unittest
import json

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app, core_engine


class TestFlaskBackend(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        core_engine.conv_store.reset_session("+91-9988776655")
        core_engine.conv_store.reset_session("+919876543210")

    def test_01_health_check(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "HEALTHY")

    def test_02_whatsapp_webhook(self):
        response = self.client.post(
            "/webhook/whatsapp",
            data={
                "MessageSid": "SM_TEST_CLEAN_001",
                "From": "whatsapp:+919876543210",
                "Body": "What is the cost of clear aligners?",
                "ProfileName": "Ananya Roy"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("<?xml", response.data.decode("utf-8"))

    def test_03_deduplication(self):
        response = self.client.post(
            "/webhook/whatsapp",
            data={
                "MessageSid": "SM_TEST_CLEAN_001",
                "From": "whatsapp:+919876543210",
                "Body": "What is the cost of clear aligners?",
                "ProfileName": "Ananya Roy"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("<Response></Response>", response.data.decode("utf-8"))

    def test_04_intake_api(self):
        response = self.client.post(
            "/api/v1/intake",
            json={
                "notes": "What is the cost of braces?",
                "name": "Test Patient",
                "phone": "+91-9988776655"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "PROCESSED_SUCCESSFULLY")


if __name__ == "__main__":
    unittest.main()
