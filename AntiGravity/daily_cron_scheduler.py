import os
import sys
import time
import datetime
import threading
import logging
from pathlib import Path

# Ensure root directory is in sys.path
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from send_pdf_to_doctor import send_pdf_report_to_doctor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DOCTOR_PHONE = "+91-7338350871"
TARGET_HOUR = 6  # 6 AM
TARGET_MINUTE = 0  # 00 mins


def run_6am_daily_loop(doctor_phone: str = DOCTOR_PHONE):
    """Background thread loop that waits until 6:00 AM every morning and dispatches the PDF report."""
    logger.info(f"⏰ Daily 6:00 AM WhatsApp PDF Dispatcher Started for Doctor ({doctor_phone})")

    while True:
        now = datetime.datetime.now()
        # Calculate target time for today's 6:00 AM
        target_time = now.replace(hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0)

        # If 6:00 AM today has already passed, schedule for tomorrow at 6:00 AM
        if now >= target_time:
            target_time += datetime.timedelta(days=1)

        seconds_until_6am = (target_time - now).total_seconds()
        logger.info(f"⏳ Next scheduled report dispatch: {target_time.strftime('%Y-%m-%d %I:%M %p')} (in {round(seconds_until_6am / 3600, 2)} hours)")

        # Sleep until 6:00 AM
        time.sleep(seconds_until_6am)

        # Execute dispatch
        logger.info("🚀 6:00 AM Reached! Executing daily patient ledger report dispatch...")
        try:
            db_url = os.getenv("DATABASE_URL", "")
            res = send_pdf_report_to_doctor(doctor_phone=doctor_phone, db_url=db_url)
            logger.info(f"✅ 6:00 AM Dispatch completed: {res.get('status')}")
        except Exception as ex:
            logger.error(f"🚨 Error executing 6:00 AM report dispatch: {ex}")

        # Sleep for 60 seconds to prevent double execution within the same minute
        time.sleep(60)


def start_automated_6am_scheduler(doctor_phone: str = DOCTOR_PHONE):
    """Starts the 6:00 AM daily scheduler in a non-blocking daemon thread."""
    t = threading.Thread(target=run_6am_daily_loop, args=(doctor_phone,), daemon=True)
    t.start()
    logger.info("✅ 6:00 AM Daily Scheduler Daemon Thread initialized.")
    return t


if __name__ == "__main__":
    print("Testing immediate 6:00 AM Daily Scheduler initialization...")
    start_automated_6am_scheduler(DOCTOR_PHONE)
    print("Scheduler running in background. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Scheduler stopped.")
