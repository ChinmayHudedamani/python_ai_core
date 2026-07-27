# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Ingress Security & Meta Webhook HMAC Sanitizer

import hmac
import hashlib
import re
import unicodedata
from typing import Optional


class IngressSanitizer:
    """OWASP-compliant input normalization & sanitizer for incoming WhatsApp choices."""

    @staticmethod
    def sanitize_choice(raw_input: str) -> str:
        """Normalizes unicode (NFC), strips non-printable control characters, and collapses whitespace."""
        if not raw_input:
            return ""

        # Normalize unicode (NFC standard)
        normalized = unicodedata.normalize("NFC", raw_input)
        
        # Strip non-printable control and format characters (category C: Cc, Cf, Cs, Co, Cn)
        cleaned = ''.join(ch for ch in normalized if not unicodedata.category(ch).startswith('C'))
        
        # Collapsing multiple whitespace gaps into a single space
        return re.sub(r'\s+', ' ', cleaned).strip()


class MetaWebhookVerifier:
    """Cryptographic HMAC-SHA256 Signature Verifier for Meta WhatsApp Cloud API."""

    @staticmethod
    def verify_signature(payload_bytes: bytes, signature_header: str, app_secret: str) -> bool:
        """Verifies incoming Meta X-Hub-Signature-256 header against app secret."""
        if not signature_header or not signature_header.startswith("sha256="):
            return False

        expected_sig = signature_header.split("sha256=")[1]
        calculated_sig = hmac.new(
            key=app_secret.encode("utf-8"),
            msg=payload_bytes,
            digestmod=hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(calculated_sig, expected_sig)


class RateLimiter:
    """Sliding-window IP / Phone Rate Limiter protecting against DoS and IDOR probes."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests = {}

    def is_allowed(self, identifier: str) -> bool:
        import time
        now = time.time()
        timestamps = self._requests.get(identifier, [])
        valid_timestamps = [ts for ts in timestamps if now - ts < self.window_seconds]

        if len(valid_timestamps) >= self.max_requests:
            self._requests[identifier] = valid_timestamps
            return False

        valid_timestamps.append(now)
        self._requests[identifier] = valid_timestamps
        return True

