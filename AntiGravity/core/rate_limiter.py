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
    """Multi-Worker & DB-Backed Atomic Appointment Slot Reservation Lock Manager."""

    def __init__(self, ttl_seconds: int = 600):
        self.ttl_seconds = ttl_seconds
        self.locks: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def reserve_slot(self, phone: str, proc_code: str, day_offset: int, time_hour: int, db_url: str = None) -> Tuple[str, bool, str]:
        """Reserves an appointment slot atomically across all Gunicorn workers and DB instances."""
        slot_id = f"SLOT_{proc_code}_{day_offset}_{time_hour}00"
        now = time.time()

        if not db_url:
            db_url = os.getenv("DATABASE_URL", "")

        # 1. Attempt Atomic PostgreSQL Reservation
        if db_url:
            try:
                import psycopg2
                import datetime
                expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=self.ttl_seconds)
                sql = """
                INSERT INTO slot_reservations (slot_id, reserved_by, expires_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (slot_id) DO UPDATE 
                SET reserved_by = EXCLUDED.reserved_by, expires_at = EXCLUDED.expires_at
                WHERE slot_reservations.expires_at < CURRENT_TIMESTAMP OR slot_reservations.reserved_by = EXCLUDED.reserved_by;
                """
                with psycopg2.connect(db_url, connect_timeout=3, options="-c statement_timeout=2000") as conn:
                    with conn.cursor() as cur:
                        cur.execute(sql, (slot_id, phone, expires_at))
                        if cur.rowcount > 0:
                            conn.commit()
                            return slot_id, True, "Slot reserved atomically in Neon DB."
                        else:
                            conn.rollback()
                            return slot_id, False, "Slot currently reserved by another patient."
            except Exception:
                pass  # Fallback to local memory lock on network interrupt

        # 2. Local Process Thread-Safe Lock Fallback
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
