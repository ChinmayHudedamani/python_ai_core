import csv
import json
import hashlib
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from day2_python import clean_client_data, mask_pii
from day4_python import generate_zero_hallucination_response

LEDGER_PATH: Path = Path(__file__).parent / "appointments_ledger.csv"

LEDGER_HEADERS: List[str] = [
    "record_hash",
    "timestamp_utc",
    "patient_name",
    "phone",
    "procedure_code",
    "lead_tier",
    "intent_score",
    "assigned_doctor",
    "booking_slot",
    "language",
    "zero_hallucination_guarantee",
    "whatsapp_response"
]


def sanitize_csv_field(field_value: Any) -> str:
    """Strips leading formula triggers (=, +, -, @) to prevent CSV Injection in Excel."""
    val_str: str = str(field_value or "").strip()
    if val_str and val_str[0] in ["=", "+", "-", "@"]:
        return f"'{val_str}"
    return val_str


def generate_record_hash(phone: str, procedure_code: str, slot: str) -> str:
    """Generates a unique SHA-256 fingerprint for record deduplication."""
    raw_key: str = f"{phone.strip()}:{procedure_code.upper().strip()}:{slot.strip()}"
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]


class OfflineLedgerWriter:
    """Idempotent CSV/Excel Offline Ledger Manager for Hospital Centaur Architecture."""

    def __init__(self, filepath: Path = LEDGER_PATH):
        self.filepath: Path = filepath
        self._ensure_ledger_initialized()

    def _ensure_ledger_initialized(self) -> None:
        """Creates the ledger CSV with schema headers if it does not exist."""
        if not self.filepath.exists():
            with open(self.filepath, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(LEDGER_HEADERS)

    def is_duplicate_record(self, record_hash: str) -> bool:
        """Checks if a record hash already exists in the ledger (O(N) file scan)."""
        if not self.filepath.exists():
            return False
        with open(self.filepath, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if not headers:
                return False
            for row in reader:
                if row and row[0] == record_hash:
                    return True
        return False

    def log_patient_intake(self, intake_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Idempotently logs a processed patient intake record into the CSV ledger.
        Returns a status dictionary indicating success, duplication, or failure.
        """
        patient: Dict[str, Any] = intake_response.get("patient", {})
        triage: Dict[str, Any] = intake_response.get("triage", {})
        grounding: Dict[str, Any] = intake_response.get("grounding_facts", {})

        phone: str = patient.get("phone", "")
        procedure_code: str = patient.get("procedure_code", "N/A")
        slots: List[str] = grounding.get("available_slots", [])
        primary_slot: str = slots[0] if slots else "PENDING_CONSULTATION"

        record_hash: str = generate_record_hash(phone, procedure_code, primary_slot)

        if self.is_duplicate_record(record_hash):
            return {
                "status": "DUPLICATE_SKIPPED",
                "record_hash": record_hash,
                "message": f"Record {record_hash} already exists in offline ledger.",
                "ledger_file": str(self.filepath)
            }

        timestamp_utc: str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        doctors: List[str] = grounding.get("matched_doctors", ["Dr. Chinmay Hudedamani"])
        assigned_doctor: str = doctors[0] if doctors else "Dr. Chinmay Hudedamani"

        row_data: List[str] = [
            record_hash,
            timestamp_utc,
            sanitize_csv_field(patient.get("name", "Unknown")),
            sanitize_csv_field(phone),
            sanitize_csv_field(procedure_code),
            sanitize_csv_field(triage.get("lead_tier", "COLD_ROUTINE")),
            str(triage.get("intent_score", 0)),
            sanitize_csv_field(assigned_doctor),
            sanitize_csv_field(primary_slot),
            sanitize_csv_field(intake_response.get("language_detected", "english")),
            str(intake_response.get("zero_hallucination_guarantee", True)),
            sanitize_csv_field(intake_response.get("whatsapp_response", ""))
        ]

        with open(self.filepath, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row_data)

        return {
            "status": "SUCCESS_LOGGED",
            "record_hash": record_hash,
            "masked_phone": mask_pii(phone),
            "ledger_file": str(self.filepath)
        }


if __name__ == "__main__":
    print("==================================================")
    print("   DAY 5: AUTOMATED OFFLINE LEDGER WRITER DEMO")
    print("==================================================\n")

    ledger = OfflineLedgerWriter()

    sample_intake = {
        "name": "Ananya Roy",
        "phone": "+919988776655",
        "procedure_code": "ALIGNERS",
        "notes": "Hi, what is the cost of invislin clear aligners in Bengaluru? Do you have EMI options?"
    }

    # Step 1: Process RAG Response
    response = generate_zero_hallucination_response(sample_intake)

    # Step 2: Log to Offline CSV Ledger
    log_result_1 = ledger.log_patient_intake(response)
    print("--- FIRST WRITE ATTEMPT ---")
    print(json.dumps(log_result_1, indent=2))

    # Step 3: Attempt Duplicate Logging (Idempotency Test)
    log_result_2 = ledger.log_patient_intake(response)
    print("\n--- SECOND WRITE ATTEMPT (IDEMPOTENCY CHECK) ---")
    print(json.dumps(log_result_2, indent=2))
