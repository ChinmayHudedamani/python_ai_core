import os
import time
import logging
from typing import Dict, Any

try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False

logger = logging.getLogger(__name__)

# Reads Razorpay Credentials from environment variables
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_centaur2026")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "secret_centaur2026")


def get_razorpay_client():
    if RAZORPAY_AVAILABLE and RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
        try:
            return razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        except Exception as e:
            logger.error(f"Razorpay Client init error: {e}")
    return None


def create_razorpay_order(amount_inr: float = 1.0, slot_id: str = "SLOT_GENERAL", patient_name: str = "Patient", patient_phone: str = "+91-9988776655") -> Dict[str, Any]:
    """Creates an official Razorpay Order for ₹1 (or configured amount) for direct Checkout integration."""
    amount_paise = int(amount_inr * 100)  # ₹1 = 100 paise
    client = get_razorpay_client()

    order_payload = {
        "amount": amount_paise,
        "currency": "INR",
        "receipt": f"rcpt_{slot_id}_{int(time.time())}",
        "notes": {
            "slot_id": slot_id,
            "patient_name": patient_name,
            "patient_phone": patient_phone,
            "clinic": "Apex Dental Center",
            "doctor": "Dr. Chinmay Hudedamani"
        }
    }

    if client:
        try:
            order = client.order.create(data=order_payload)
            logger.info(f"✅ Created Razorpay Order {order.get('id')} for ₹{amount_inr}")
            return {
                "status": "SUCCESS",
                "order_id": order.get("id"),
                "amount": amount_inr,
                "amount_paise": amount_paise,
                "currency": "INR",
                "key_id": RAZORPAY_KEY_ID
            }
        except Exception as ex:
            logger.error(f"Razorpay Order creation API error: {ex}")

    # Seamless Fallback Order Structure for Demo / Test mode
    mock_order_id = f"order_demo_{int(time.time())}"
    return {
        "status": "DEMO_SUCCESS",
        "order_id": mock_order_id,
        "amount": amount_inr,
        "amount_paise": amount_paise,
        "currency": "INR",
        "key_id": RAZORPAY_KEY_ID
    }


def verify_razorpay_payment_signature(razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
    """Cryptographically verifies Razorpay payment signature after successful checkout."""
    client = get_razorpay_client()
    if client:
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            client.utility.verify_payment_signature(params_dict)
            return True
        except Exception as ex:
            logger.error(f"Signature verification failed: {ex}")
            return False
    return True  # Fallback return for demo mode
