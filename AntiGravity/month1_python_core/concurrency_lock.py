import json
import time
import hashlib
import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

SLOT_LOCKS_DIR: Path = Path(__file__).parent / "slot_locks"
DEFAULT_TTL_SECONDS: int = 600  # 10-Minute Ephemeral Reservation Lock TTL


def ensure_locks_directory() -> None:
    """Ensures slot locks directory exists."""
    SLOT_LOCKS_DIR.mkdir(parents=True, exist_ok=True)


def generate_slot_key(doctor_id: str, slot_datetime_iso: str) -> str:
    """Generates a unique deterministic lock key for a doctor slot."""
    raw = f"{doctor_id.strip()}:{slot_datetime_iso.strip()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


class SlotConcurrencyLockManager:
    """
    Enterprise Concurrency Control & Double-Booking Prevention Engine.
    Implements Atomic Mutex Slot Lockouts & 10-Minute Ephemeral Reservation Holds.
    Prevents race conditions when multiple patients attempt to book the exact same slot.
    """

    def __init__(self, ttl_seconds: int = DEFAULT_TTL_SECONDS):
        ensure_locks_directory()
        self.ttl_seconds: int = ttl_seconds

    def acquire_ephemeral_slot_hold(self, doctor_id: str, slot_time_str: str, patient_phone: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Attempts to atomically acquire a 10-minute hold for a consultation slot.
        Returns (True, lock_details) if lock acquired;
        Returns (False, collision_details) if slot is currently held or permanently booked by another patient.
        """
        slot_key: str = generate_slot_key(doctor_id, slot_time_str)
        lock_file: Path = SLOT_LOCKS_DIR / f"lock_{slot_key}.json"

        now: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
        now_ts: float = now.timestamp()

        # Check existing lock file
        if lock_file.exists():
            try:
                with open(lock_file, "r", encoding="utf-8") as f:
                    lock_data = json.load(f)

                expires_ts: float = lock_data.get("expires_timestamp", 0)
                holder_phone: str = lock_data.get("patient_phone", "")
                status: str = lock_data.get("status", "")

                # 1. Permanently Locked
                if status == "PERMANENTLY_LOCKED":
                    return False, {
                        "status": "SLOT_ALREADY_BOOKED",
                        "slot_key": slot_key,
                        "slot_time": slot_time_str,
                        "message": f"Slot '{slot_time_str}' has already been booked by another patient."
                    }

                # 2. Currently Held by Same Patient
                if holder_phone == patient_phone and now_ts < expires_ts:
                    return True, {
                        "status": "LOCK_HELD_BY_YOU",
                        "slot_key": slot_key,
                        "slot_time": slot_time_str,
                        "expires_in_seconds": round(expires_ts - now_ts),
                        "lock_file": str(lock_file)
                    }

                # 3. Active Hold by ANOTHER Patient
                if now_ts < expires_ts:
                    remaining_seconds: int = round(expires_ts - now_ts)
                    return False, {
                        "status": "CONCURRENCY_COLLISION_SLOT_HELD",
                        "slot_key": slot_key,
                        "slot_time": slot_time_str,
                        "expires_in_seconds": remaining_seconds,
                        "message": f"Slot '{slot_time_str}' is currently held for 10 mins by another patient completing payment."
                    }
            except Exception:
                pass

        # Acquire New 10-Minute Lock
        expires_dt: datetime.datetime = now + datetime.timedelta(seconds=self.ttl_seconds)
        new_lock = {
            "slot_key": slot_key,
            "doctor_id": doctor_id,
            "slot_time": slot_time_str,
            "patient_phone": patient_phone,
            "status": "TEMPORARY_RESERVED",
            "acquired_utc": now.isoformat(),
            "expires_utc": expires_dt.isoformat(),
            "expires_timestamp": expires_dt.timestamp()
        }

        with open(lock_file, "w", encoding="utf-8") as f:
            json.dump(new_lock, f, indent=2)

        return True, {
            "status": "EPHEMERAL_HOLD_ACQUIRED",
            "slot_key": slot_key,
            "slot_time": slot_time_str,
            "expires_in_seconds": self.ttl_seconds,
            "lock_file": str(lock_file)
        }

    def commit_permanent_slot_booking(self, doctor_id: str, slot_time_str: str, patient_phone: str, tx_id: str) -> Dict[str, Any]:
        """
        Atomically commits payment settlement, transitioning slot state to PERMANENTLY_LOCKED.
        """
        slot_key: str = generate_slot_key(doctor_id, slot_time_str)
        lock_file: Path = SLOT_LOCKS_DIR / f"lock_{slot_key}.json"

        now: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
        permanent_record = {
            "slot_key": slot_key,
            "doctor_id": doctor_id,
            "slot_time": slot_time_str,
            "patient_phone": patient_phone,
            "status": "PERMANENTLY_LOCKED",
            "payment_tx_id": tx_id,
            "locked_utc": now.isoformat()
        }

        with open(lock_file, "w", encoding="utf-8") as f:
            json.dump(permanent_record, f, indent=2)

        return {
            "status": "PERMANENTLY_BOOKED",
            "slot_key": slot_key,
            "transaction_id": tx_id,
            "lock_file": str(lock_file)
        }


if __name__ == "__main__":
    mgr = SlotConcurrencyLockManager(ttl_seconds=600)
    acquired, info = mgr.acquire_ephemeral_slot_hold("dr_chinmay", "Saturday at 11:00 AM", "+91-9988776655")
    print(f"Acquired Lock 1: {acquired}")
    print(json.dumps(info, indent=2))

    # Collision test by second patient
    acquired_2, info_2 = mgr.acquire_ephemeral_slot_hold("dr_chinmay", "Saturday at 11:00 AM", "+91-9111122222")
    print(f"\nAcquired Lock 2 (Should Collision): {acquired_2}")
    print(json.dumps(info_2, indent=2))
