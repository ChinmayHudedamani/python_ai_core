import os
import sys
import io
import time
import uuid
from pathlib import Path

# Force UTF-8 encoding for Windows terminal output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure root directory is in sys.path
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from clinical.ledger_writer import log_appointment, init_db, get_db_url
from core.engine import CentaurCoreEngine

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

TEST_CASES = [
    {
        "name": "Rahul Sharma",
        "phone": "+91-9876543210",
        "procedure": "Root Canal Treatment (RCT)",
        "notes": "Severe molar pain on right side, needs immediate RCT",
        "slot": "Tomorrow 10:00 AM"
    },
    {
        "name": "Priya Patel",
        "phone": "+91-9823456789",
        "procedure": "Teeth Whitening & Laser Polishing",
        "notes": "Laser teeth whitening consultation before wedding",
        "slot": "Tomorrow 11:30 AM"
    },
    {
        "name": "Vikramaditya Rao",
        "phone": "+91-9711223344",
        "procedure": "Clear Aligners Consultation",
        "notes": "Invisalign aligner scan and price estimation",
        "slot": "Tomorrow 02:00 PM"
    },
    {
        "name": "Ananya Sen",
        "phone": "+91-9654321098",
        "procedure": "Dental Implant Evaluation",
        "notes": "Single tooth replacement evaluation with 3D CBCT scan",
        "slot": "Tomorrow 04:00 PM"
    },
    {
        "name": "Rajesh Gupta",
        "phone": "+91-9543210987",
        "procedure": "Wisdom Tooth Extraction",
        "notes": "Impacted lower left wisdom tooth swelling",
        "slot": "Day After 09:30 AM"
    },
    {
        "name": "Sneha Reddy",
        "phone": "+91-9432109876",
        "procedure": "Emergency Toothache & Filling",
        "notes": "Broken composite filling causing sensitivity",
        "slot": "Today 06:00 PM"
    },
    {
        "name": "Amit Kumar",
        "phone": "+91-9321098765",
        "procedure": "Routine Scaling & Cleaning",
        "notes": "Bi-annual tartar removal and dental checkup",
        "slot": "Day After 11:00 AM"
    },
    {
        "name": "Kavita Joshi",
        "phone": "+91-9210987654",
        "procedure": "Porcelain Veneers Consultation",
        "notes": "Smile design consultation for front upper teeth",
        "slot": "Day After 03:00 PM"
    },
    {
        "name": "Rohan Mehta",
        "phone": "+91-9109876543",
        "procedure": "Zirconia Crown Fitting",
        "notes": "Crown placement after root canal treatment",
        "slot": "Day After 05:00 PM"
    },
    {
        "name": "Deepa Nair",
        "phone": "+91-9098765432",
        "procedure": "Pediatric Dental Checkup",
        "notes": "Cavity checkup and fluoride application for 7yo child",
        "slot": "Saturday 10:00 AM"
    }
]


def run_test_suite(db_url: str = None):
    if db_url:
        os.environ["DATABASE_URL"] = db_url

    current_db_url = get_db_url()
    if not current_db_url:
        print("\n[!] DATABASE_URL environment variable is not set. Running in Offline Local CSV Fallback Mode.")
        db_url_input = os.getenv("DATABASE_URL", "").strip()
        if db_url_input:
            os.environ["DATABASE_URL"] = db_url_input
            current_db_url = db_url_input

    print("==========================================================================")
    print("      CENTAUR OS - WHATSAPP DEMO BOT 10 TEST CASES RUNNER                ")
    print("==========================================================================")
    print(f"Target Database: Neon Serverless PostgreSQL\n")

    # Initialize DB connection and schema
    init_db()

    engine = CentaurCoreEngine()
    results = []

    for idx, tc in enumerate(TEST_CASES, 1):
        print(f"--- [TEST CASE {idx}/10]: {tc['name']} ({tc['procedure']}) ---")
        print(f"📱 Patient Phone: {tc['phone']}")
        print(f"💬 Initial Inquiry: '{tc['notes']}'")

        # Step 1: Process WhatsApp Message Intake
        intake_res = engine.process_patient_intake(
            raw_notes=f"Hi, I am {tc['name']}. Phone: {tc['phone']}. {tc['notes']}",
            patient_name=tc['name'],
            patient_phone=tc['phone']
        )
        print(f"🤖 Bot Response Status: {intake_res.get('status')}")

        # Step 2: Simulate Payment Confirmation & DB Record Creation
        txn_id = f"TXN_DEMO_{idx:03d}_{int(time.time())}"
        slot_notes = f"{tc['procedure']} | Slot: {tc['slot']}"

        ledger_res = log_appointment(
            patient_number=tc['phone'],
            time_slot=slot_notes,
            procedure_type=tc['procedure'],
            transaction_id=txn_id,
            patient_name=tc['name']
        )

        print(f"💾 Neon DB Write Result: {ledger_res.get('status')} | SHA256: {ledger_res.get('sha256', '')[:16]}...")
        print("-" * 74)
        results.append((tc['name'], tc['phone'], tc['procedure'], txn_id, ledger_res.get('status')))
        time.sleep(0.3)

    print("\n==========================================================================")
    print("                      SUMMARY OF 10 TEST CASES                            ")
    print("==========================================================================")
    for r in results:
        print(f"✅ Patient: {r[0]:<20} | Phone: {r[1]:<15} | Txn: {r[3]:<25} | DB Status: {r[4]}")

    # Step 3: Fetch and display actual records directly from Neon PostgreSQL
    if PSYCOPG2_AVAILABLE and current_db_url:
        print("\n==========================================================================")
        print("         FETCHING LIVE RECORDS FROM NEON DATABASE (appointments_ledger)   ")
        print("==========================================================================")
        try:
            with psycopg2.connect(current_db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id, patient_number, procedure_type, transaction_id, created_at FROM appointments_ledger ORDER BY created_at DESC LIMIT 10;")
                    rows = cur.fetchall()
                    print(f"Total Rows Fetched from Neon: {len(rows)}\n")
                    for row in rows:
                        print(f"📌 ID: {row[0]}")
                        print(f"   Patient Phone : {row[1]}")
                        print(f"   Procedure     : {row[2]}")
                        print(f"   Transaction ID: {row[3]}")
                        print(f"   Created At    : {row[4]}")
                        print("   " + "-" * 60)
        except Exception as e:
            print(f"Error querying Neon DB: {e}")


if __name__ == "__main__":
    url_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_test_suite(url_arg)
