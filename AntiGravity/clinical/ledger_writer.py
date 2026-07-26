import os
import csv
import hashlib
import datetime
from pathlib import Path
from typing import Dict, Any

LEDGER_FILE = Path(__file__).parent.parent / "appointments_ledger.csv"


class OfflineLedgerWriter:
    """CSV Ledger Recorder with SHA-256 Cryptographic Hash Verification."""

    def __init__(self):
        self.ledger_file = LEDGER_FILE
        self._ensure_ledger_initialized()

    def _ensure_ledger_initialized(self) -> None:
        if not self.ledger_file.exists():
            with open(self.ledger_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp_iso",
                    "patient_name",
                    "patient_phone",
                    "procedure_code",
                    "raw_notes",
                    "hash_sha256"
                ])

    def calculate_sha256(self, timestamp: str, name: str, phone: str, proc: str, notes: str) -> str:
        raw_str = f"{timestamp}|{name}|{phone}|{proc}|{notes}"
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

    def write_appointment_lead(self, name: str, phone: str, procedure_code: str, raw_notes: str) -> Dict[str, Any]:
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        hash_val = self.calculate_sha256(timestamp, name, phone, procedure_code, raw_notes)

        row = [timestamp, name, phone, procedure_code, raw_notes, hash_val]
        try:
            with open(self.ledger_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(row)
            return {"status": "SUCCESS", "sha256": hash_val, "ledger_file": str(self.ledger_file)}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
