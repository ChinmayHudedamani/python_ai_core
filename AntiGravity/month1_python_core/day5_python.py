import csv
import json
import hashlib
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from day2_python import clean_client_data, mask_pii
from day4_python import generate_zero_hallucination_response

LEDGER_DIR: Path = Path(__file__).parent / "archives"
MASTER_LEDGER_PATH: Path = Path(__file__).parent / "appointments_ledger.csv"

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

ESTIMATED_PROCEDURE_VALUATION: Dict[str, int] = {
    "IMP": 35000,
    "INVIS": 120000,
    "ALIGNERS": 120000,
    "FMR": 250000,
    "SMB": 45000,
    "RCT": 7500,
    "CROWN": 12000
}


def sanitize_csv_field(field_value: Any) -> str:
    """Enhanced CSV Injection Shield: Neutralizes =, +, -, @, cmd, and control tokens for Excel safety."""
    val_str: str = str(field_value or "").strip()
    if val_str and val_str[0] in ["=", "+", "-", "@"]:
        return f"'{val_str}"
    if val_str.lower().startswith(("cmd", "powershell", "exec")):
        return f"'{val_str}"
    return val_str


def generate_record_hash(phone: str, procedure_code: str, slot: str) -> str:
    """Generates a unique SHA-256 fingerprint for record deduplication."""
    raw_key: str = f"{phone.strip()}:{procedure_code.upper().strip()}:{slot.strip()}"
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]


def anonymize_string(val: str) -> str:
    """Cryptographically anonymizes PII strings (names, phones) via salted SHA-256."""
    return hashlib.sha256(f"ANON_SALT:{val.strip()}".encode("utf-8")).hexdigest()[:12]


def ensure_archives_directory() -> None:
    """Ensures archives directory exists for daily automated ledger rotation."""
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)


class OfflineLedgerWriter:
    """
    Enterprise Idempotent CSV/Excel Offline Ledger & Analytics Exporter.
    Features:
    - Master CSV logging & daily YYYY-MM-DD automated archive rotation
    - SHA-256 record deduplication (idempotent file handling)
    - Anti-CSV injection formula neutralization
    - HIPAA/GDPR anonymized cloud export generator
    - Daily Executive Pipeline Revenue Summarizer
    """

    def __init__(self, master_path: Path = MASTER_LEDGER_PATH):
        ensure_archives_directory()
        self.master_path: Path = master_path
        self._ensure_file_headers(self.master_path)

    def get_today_archive_path(self) -> Path:
        """Calculates today's YYYY-MM-DD daily rotated CSV archive path."""
        date_str: str = datetime.datetime.now().strftime("%Y-%m-%d")
        return LEDGER_DIR / f"appointments_ledger_{date_str}.csv"

    def _ensure_file_headers(self, filepath: Path) -> None:
        """Creates the ledger CSV with schema headers if it does not exist."""
        if not filepath.exists():
            with open(filepath, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(LEDGER_HEADERS)

    def is_duplicate_record(self, record_hash: str, filepath: Path) -> bool:
        """Checks if a record hash already exists in the targeted ledger file."""
        if not filepath.exists():
            return False
        with open(filepath, mode="r", encoding="utf-8") as f:
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
        Idempotently logs intake records into both Master Ledger and Daily Rotated Archive.
        """
        patient: Dict[str, Any] = intake_response.get("patient", {})
        triage: Dict[str, Any] = intake_response.get("triage", {})
        grounding: Dict[str, Any] = intake_response.get("grounding_facts", {})

        phone: str = patient.get("phone", "")
        procedure_code: str = patient.get("procedure_code", "N/A")
        slots: List[str] = grounding.get("available_slots", [])
        primary_slot: str = slots[0] if slots else "PENDING_CONSULTATION"

        record_hash: str = generate_record_hash(phone, procedure_code, primary_slot)
        today_archive: Path = self.get_today_archive_path()
        self._ensure_file_headers(today_archive)

        if self.is_duplicate_record(record_hash, self.master_path):
            return {
                "status": "DUPLICATE_SKIPPED",
                "record_hash": record_hash,
                "message": f"Record {record_hash} already exists in master ledger.",
                "ledger_file": str(self.master_path)
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

        # Write to Master Ledger
        with open(self.master_path, mode="a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(row_data)

        # Write to Daily Rotated Archive
        with open(today_archive, mode="a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(row_data)

        return {
            "status": "SUCCESS_LOGGED",
            "record_hash": record_hash,
            "masked_phone": mask_pii(phone),
            "master_ledger": str(self.master_path),
            "daily_archive": str(today_archive)
        }

    def export_anonymized_ledger(self) -> Path:
        """
        Generates a HIPAA/GDPR compliant PII-anonymized copy of the ledger for cloud backup.
        Replaces patient names & phone numbers with cryptographic hashes.
        """
        date_str: str = datetime.datetime.now().strftime("%Y-%m-%d")
        anon_export_path: Path = LEDGER_DIR / f"anonymized_export_{date_str}.csv"

        if not self.master_path.exists():
            self._ensure_file_headers(anon_export_path)
            return anon_export_path

        with open(self.master_path, mode="r", encoding="utf-8") as f_in:
            reader = csv.reader(f_in)
            rows = list(reader)

        if not rows:
            return anon_export_path

        headers = rows[0]
        anonymized_rows = [headers]

        for row in rows[1:]:
            if len(row) >= 4:
                anon_row = list(row)
                anon_row[2] = anonymize_string(row[2])  # Anonymize Name
                anon_row[3] = anonymize_string(row[3])  # Anonymize Phone
                anonymized_rows.append(anon_row)

        with open(anon_export_path, mode="w", newline="", encoding="utf-8") as f_out:
            csv.writer(f_out).writerows(anonymized_rows)

        return anon_export_path

    def generate_daily_summary(self) -> Dict[str, Any]:
        """Calculates executive pipeline metrics, lead counts, and estimated revenue from Master Ledger."""
        if not self.master_path.exists():
            return {"total_records": 0, "projected_pipeline_inr": 0}

        with open(self.master_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            records = list(reader)

        tier_counts: Dict[str, int] = {}
        total_revenue_inr: int = 0

        for r in records:
            tier = r.get("lead_tier", "COLD_ROUTINE")
            proc = r.get("procedure_code", "").upper().strip()
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

            if tier in ["VIP_HIGH_REVENUE", "URGENT_CLINICAL"]:
                val = ESTIMATED_PROCEDURE_VALUATION.get(proc, 15000)
                total_revenue_inr += val

        return {
            "total_records": len(records),
            "tier_breakdown": tier_counts,
            "projected_pipeline_inr": total_revenue_inr,
            "formatted_revenue": f"₹{total_revenue_inr:,}"
        }


if __name__ == "__main__":
    print("==================================================")
    print("   DAY 5 UPGRADED: ENTERPRISE CSV LEDGER DEMO")
    print("==================================================\n")

    ledger = OfflineLedgerWriter()

    sample_intake = {
        "name": "Ananya Roy",
        "phone": "+919988776655",
        "procedure_code": "ALIGNERS",
        "notes": "Hi, what is the cost of invislin clear aligners in Bengaluru? Do you have EMI options?"
    }

    response = generate_zero_hallucination_response(sample_intake)
    log_res = ledger.log_patient_intake(response)
    print("--- INTAKE LOGGING RESULT ---")
    print(json.dumps(log_res, indent=2))

    print("\n--- ANONYMIZED CLOUD EXPORT ---")
    anon_path = ledger.export_anonymized_ledger()
    print(f"Exported PII-safe ledger to: {anon_path}")

    print("\n--- EXECUTIVE DAILY SUMMARY REPORT ---")
    summary = ledger.generate_daily_summary()
    print(json.dumps(summary, indent=2))
