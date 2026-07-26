import time
import threading
from typing import Dict, Any, Tuple, Optional


class TokenBucketRateLimiter:
    """Thread-safe Token Bucket Rate Limiter for Patient Phone Numbers."""

    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
        self.lock = threading.Lock()

    def is_rate_limited(self, phone: str) -> Tuple[bool, str]:
        """Returns True if phone has exceeded rate limit window."""
        now = time.time()
        with self.lock:
            if phone not in self.requests:
                self.requests[phone] = []

            # Filter timestamps within window
            self.requests[phone] = [ts for ts in self.requests[phone] if now - ts < self.window_seconds]

            if len(self.requests[phone]) >= self.max_requests:
                return True, "Rate limit exceeded (5 requests/min). Please wait 60 seconds before trying again."

            self.requests[phone].append(now)
            return False, ""


class SlotConcurrencyLockManager:
    """Thread-safe Appointment Slot Reservation Lock Manager."""

    def __init__(self, ttl_seconds: int = 600):
        self.ttl_seconds = ttl_seconds
        self.locks: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def reserve_slot(self, phone: str, proc_code: str, day_offset: int, time_hour: int) -> Tuple[str, bool, str]:
        """Reserves an appointment slot for a patient."""
        slot_id = f"SLOT_{proc_code}_{day_offset}_{time_hour}00"
        now = time.time()

        with self.lock:
            if slot_id in self.locks:
                lock_info = self.locks[slot_id]
                if now - lock_info["created_at"] < self.ttl_seconds and lock_info["phone"] != phone:
                    return slot_id, False, "Slot currently locked by another reservation."

            self.locks[slot_id] = {
                "phone": phone,
                "created_at": now
            }
            return slot_id, True, "Slot reservation locked successfully."
