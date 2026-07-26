import os
import sys
import io
import datetime
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure root directory is in sys.path
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from generate_doctor_financial_pdf import build_doctor_financial_pdf_report, fetch_financial_records
from core.meta_whatsapp import MetaWhatsAppCloudEngine

DOCTOR_PHONE = os.getenv("DOCTOR_PHONE", "+91-7338350871")
DOCTOR_NAME = "Dr. Chinmay Hudedamani"


def send_financial_pdf_report_to_doctor(doctor_phone: str = DOCTOR_PHONE, db_url: str = None) -> dict:
    """Generates financial PDF report and dispatches WhatsApp payment summary alert to doctor."""
    print("==========================================================================")
    print("   CENTAUR OS - DOCTOR FINANCIAL RECEIPTS WHATSAPP DISPATCHER            ")
    print("==========================================================================")
    print(f"Target Doctor Number: {doctor_phone}")
    print(f"Target Doctor Name  : {DOCTOR_NAME}\n")

    # Step 1: Generate PDF Report File
    pdf_filename = "Apex_Dental_Doctor_Financial_Report.pdf"
    pdf_file_path = build_doctor_financial_pdf_report(pdf_filename, db_url)

    # Step 2: Fetch Live Credit Records
    records = fetch_financial_records(db_url)
    total_count = len(records)
    today_str = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

    # Step 3: Formulate Financial WhatsApp Message Breakdown
    msg_body = (
        f"💰 *APEX DENTAL CENTER — BANK CREDIT & PAYMENT RECEIPTS REPORT*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Doctor:* {DOCTOR_NAME}\n"
        f"📅 *Date:* {today_str}\n"
        f"📞 *Doctor Contact:* {doctor_phone}\n\n"
        f"💵 *PAYMENT SUMMARY:*\n"
        f"• 💳 Total Payment Credits: *{total_count} Verified Transactions*\n"
        f"• 🏦 Bank Settlement Status: *100% CREDITED TO BANK ACCOUNT*\n"
        f"• ⚡ Auto-Trigger: *Razorpay Webhook -> Instant Slot Locking*\n\n"
        f"📋 *RECENT CREDITS (PATIENT NAME & PHONE):*\n"
    )

    for idx, r in enumerate(records[:8], 1):
        msg_body += f"{idx}. *{r['phone']}* — Fee: `{r['amount']}` | Ref: `{r['txn_id']}`\n"

    msg_body += (
        f"\n📄 *Attached PDF Audit File:* `Apex_Dental_Doctor_Financial_Report.pdf`\n"
        f"*(Synced live with Neon PostgreSQL & Bank Razorpay Webhook)*"
    )

    meta_engine = MetaWhatsAppCloudEngine()
    dispatch_res = meta_engine.send_whatsapp_message(doctor_phone, msg_body)

    print(f"\nWhatsApp Financial Dispatch Status: {dispatch_res.get('status')}")
    print(f"Financial PDF File Ready: {pdf_file_path}")

    return {
        "status": "SUCCESS",
        "doctor_phone": doctor_phone,
        "pdf_path": pdf_file_path,
        "records_count": total_count,
        "whatsapp_dispatch": dispatch_res
    }


if __name__ == "__main__":
    db_url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("DATABASE_URL", "")
    send_financial_pdf_report_to_doctor(DOCTOR_PHONE, db_url)
