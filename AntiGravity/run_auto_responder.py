import sys
import time
import json
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Set, Dict, Any

sys.path.insert(0, str(Path(__file__).parent / "month1_python_core"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from twilio_live_polling import fetch_latest_inbound_messages, breaker, dispatcher
from twilio_config import load_twilio_credentials

DEDUP_CACHE_FILE = Path(__file__).parent / "processed_sids.txt"
file_lock = threading.Lock()
processed_sids_lock = threading.Lock()


def load_processed_sids() -> Set[str]:
    """Loads historical processed SIDs to prevent duplicate responses across restarts."""
    if DEDUP_CACHE_FILE.exists():
        with open(DEDUP_CACHE_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_processed_sid(msg_sid: str) -> None:
    """Thread-safe append of newly processed SID to persistent cache file."""
    with file_lock:
        with open(DEDUP_CACHE_FILE, "a", encoding="utf-8") as f:
            f.write(f"{msg_sid}\n")


def is_recent_message(date_created_str: str, max_age_seconds: int = 45) -> bool:
    """Verifies if the message was created in the last 45 seconds to prevent old retries."""
    try:
        created_dt = datetime.datetime.strptime(date_created_str, "%a, %d %b %Y %H:%M:%S %z")
        now_dt = datetime.datetime.now(datetime.timezone.utc)
        age = (now_dt - created_dt).total_seconds()
        return age <= max_age_seconds
    except Exception:
        return True


def process_single_patient_message(msg: Dict[str, Any]) -> None:
    """
    Worker Thread Function.
    Processes an individual patient message safely.
    """
    msg_sid = msg.get("sid", "")
    date_created = msg.get("date_created", "")

    if not is_recent_message(date_created, max_age_seconds=45):
        print(f"  ⏭️ Skipped old message SID: {msg_sid} (Created: {date_created})")
        return

    from_phone = msg.get("from", "").replace("whatsapp:", "").strip()
    body_text = msg.get("body", "").strip()

    now_str = datetime.datetime.now().strftime("%I:%M:%S %p")
    thread_name = threading.current_thread().name
    print(f"[{now_str}] 📩 [{thread_name}] PROCESSING LIVE MESSAGE (SID: {msg_sid}) from {from_phone}: \"{body_text}\"")

    raw_intake = {
        "name": "Patient",
        "phone": from_phone,
        "procedure_code": "GENERAL",
        "notes": body_text
    }

    # Parallel Execution through Centaur OS RAG Engine
    start_t = time.time()
    result = breaker.process_intake_safety_circuit(raw_intake, force_fast_rag=True)
    reply_text = result.get("whatsapp_response", "")
    exec_ms = round((time.time() - start_t) * 1000, 2)

    # Thread-Safe Outbound WhatsApp Dispatch
    disp_res = dispatcher.send_whatsapp_message(from_phone, reply_text)
    print(f"[{now_str}] ⚡ [{thread_name}] DISPATCHED SINGLE REPLY to {from_phone} in {exec_ms} ms (Outbound SID: {disp_res.get('sid')})\n")


def start_enterprise_concurrency_auto_responder():
    creds = load_twilio_credentials()
    sid = creds.get("account_sid", "")
    token = creds.get("auth_token", "")
    processed_sids = load_processed_sids()

    print("\n==================================================")
    print(" 🚀 CENTAUR CLINIC ATOMIC SINGLE-DISPATCH ENGINE")
    print(f" 🟢 Loaded {len(processed_sids)} historical message SIDs")

    # Prime historical SIDs
    initial_msgs = fetch_latest_inbound_messages(sid, token)
    primed_count = 0
    with processed_sids_lock:
        for m in initial_msgs:
            m_sid = m.get("sid", "")
            if m_sid and m_sid not in processed_sids:
                processed_sids.add(m_sid)
                save_processed_sid(m_sid)
                primed_count += 1

    print(f" 🛡️ Primed & Locked {primed_count} past messages.")
    print(" ⚡ Atomic Mutex Lock Active: Guaranteed EXACTLY 1 reply per message SID.")
    print("==================================================\n")

    executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="PatientWorker")

    while True:
        try:
            inbound_msgs = fetch_latest_inbound_messages(sid, token)
            for msg in inbound_msgs:
                m_sid = msg.get("sid", "")

                # ATOMIC MAIN THREAD CHECK AND LOCK BEFORE SUBMISSION
                with processed_sids_lock:
                    if m_sid and m_sid not in processed_sids:
                        processed_sids.add(m_sid)
                        save_processed_sid(m_sid)
                        executor.submit(process_single_patient_message, msg)
        except Exception as e:
            print(f"⚠️ Polling loop error: {e}")

        time.sleep(2)


if __name__ == "__main__":
    start_enterprise_concurrency_auto_responder()
