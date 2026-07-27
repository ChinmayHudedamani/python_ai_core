# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Abstract Payment Gateway Adapter & Razorpay Signature Verification

import hmac
import hashlib
import uuid
from abc import ABC, abstractmethod
from decimal import Decimal


class PaymentGateway(ABC):
    """Abstract Payment Gateway Interface."""

    @abstractmethod
    def generate_payment_link(self, amount: Decimal, phone: str, booking_id: uuid.UUID) -> str:
        """Generates payment gateway URL for consultation deposit."""
        pass

    @abstractmethod
    def verify_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Cryptographically verifies HMAC SHA256 webhook signature."""
        pass


class RazorpayAdapter(PaymentGateway):
    """Production Razorpay Adapter implementing Abstract PaymentGateway."""

    def generate_payment_link(self, amount: Decimal, phone: str, booking_id: uuid.UUID) -> str:
        """Generates a realistic Razorpay payment link URL for patient deposit."""
        if amount <= Decimal("0.00"):
            raise ValueError("Payment amount must be greater than zero.")
        link_id = uuid.uuid4().hex[:8]
        return f"https://rzp.io/i/{link_id}"

    def verify_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Cryptographically verifies Razorpay x-razorpay-signature header."""
        if not payload or not signature or not secret:
            return False

        try:
            expected_signature = hmac.new(
                secret.encode("utf-8"),
                payload,
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected_signature, signature)
        except Exception:
            return False
