import os
import sys
import time
import threading
import traceback
from typing import Dict, Any
from flask import Flask, request, Response, jsonify
from flask_cors import CORS

# Add parent directory to path to ensure clean imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core_engine import CentaurCoreEngine
from day5_python import OfflineLedgerWriter

# Initialize Flask Application with Production CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Core Engine & Ledger Singletons
core_engine = CentaurCoreEngine()
ledger_writer = OfflineLedgerWriter()

# Atomic In-Memory Message Deduplication Lock
processed_sids = set()
sid_lock = threading.Lock()
start_timestamp = time.time()


@app.errorhandler(404)
def handle_404_not_found(e):
    """Fail-Safe 404 Route Handler."""
    return jsonify({"status": "NOT_FOUND", "message": "Resource endpoint does not exist."}), 404


@app.errorhandler(405)
def handle_405_method_not_allowed(e):
    """Fail-Safe 405 Method Handler."""
    return jsonify({"status": "METHOD_NOT_ALLOWED", "message": "HTTP method not allowed for this route."}), 405


@app.errorhandler(Exception)
def handle_global_exception(e):
    """
    Unbreakable Global Catch-All Exception Handler.
    Guarantees the Flask backend NEVER crashes or drops connection under any unhandled exception.
    """
    error_msg = str(e)
    stack_trace = traceback.format_exc()
    print(f"  🚨 [UNBREAKABLE RECOVERY]: {error_msg}\n{stack_trace}")

    if request.path.startswith("/webhook/whatsapp"):
        # Return valid empty TwiML XML to Twilio so webhook does not retry
        return Response('<?xml version="1.0" encoding="UTF-8"?><Response></Response>', mimetype="text/xml")

    return jsonify({
        "status": "ERROR_RECOVERED",
        "error": error_msg,
        "timestamp": time.time()
    }), 200


@app.route("/", methods=["GET"])
def health_check():
    """System Health Check & Uptime Endpoint (Compatible with Render/Railway Cloud Health Probes)."""
    uptime_seconds = round(time.time() - start_timestamp, 2)
    return jsonify({
        "status": "HEALTHY",
        "system": "Centaur OS Unbreakable Enterprise Backend",
        "uptime_seconds": uptime_seconds,
        "active_threads": threading.active_count(),
        "deduplicated_sids_count": len(processed_sids),
        "port": int(os.getenv("PORT", 5000))
    }), 200


@app.route("/webhook/whatsapp", methods=["POST", "GET"])
def whatsapp_webhook():
    """
    Production Fail-Safe WhatsApp Webhook Endpoint.
    Intercepts Twilio webhooks, handles atomic deduplication, processes patient intake,
    and returns single-payload TwiML XML instantly.
    """
    if request.method == "GET":
        return Response('<?xml version="1.0" encoding="UTF-8"?><Response><Message>Centaur OS Webhook Online</Message></Response>', mimetype="text/xml")

    form_data = request.form
    msg_sid = form_data.get("MessageSid", "").strip()
    from_number = form_data.get("From", "").replace("whatsapp:", "").strip()
    body_text = form_data.get("Body", "").strip()
    profile_name = form_data.get("ProfileName", "Patient").strip()

    if not body_text:
        return Response('<?xml version="1.0" encoding="UTF-8"?><Response></Response>', mimetype="text/xml")

    # Atomic Memory Deduplication Check
    if msg_sid:
        with sid_lock:
            if msg_sid in processed_sids:
                print(f"  ⏭️ [DEDUPLICATED Webhook Retry] SID: {msg_sid}")
                return Response('<?xml version="1.0" encoding="UTF-8"?><Response></Response>', mimetype="text/xml")
            processed_sids.add(msg_sid)

    print(f"\n📩 [INCOMING WHATSAPP] From: {profile_name} ({from_number}) | Body: '{body_text}'")

    # Process Patient Intake through Core Pipeline
    try:
        pipeline_result = core_engine.process_patient_intake(
            raw_notes=body_text,
            patient_name=profile_name,
            patient_phone=from_number
        )
        reply_text = pipeline_result.get("whatsapp_response", "Thank you for contacting Apex Dental Center. Our team will contact you shortly.")
    except Exception as ex:
        print(f"  ⚠️ [Pipeline Fallback Triggered]: {ex}")
        reply_text = f"Hello {profile_name},\n\nThank you for contacting Apex Dental Center.\nOur clinic is currently open from 9:00 AM to 8:00 PM in Koramangala.\nDoctor: Dr. Chinmay Hudedamani.\n\nPlease reply with your requested service to assist you further."

    twiml_response = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply_text}</Message></Response>'
    return Response(twiml_response, mimetype="text/xml")


@app.route("/api/v1/intake", methods=["POST"])
def patient_intake_api():
    """Synchronous Patient Intake REST API for Web Widgets & Front-Desk Applications."""
    data = request.get_json(force=True, silent=True) or {}
    notes = data.get("notes", "")
    patient_name = data.get("name", "Patient")
    patient_phone = data.get("phone", "+91-9988776655")

    if not notes:
        return jsonify({"status": "ERROR", "message": "Field 'notes' is required."}), 400

    result = core_engine.process_patient_intake(
        raw_notes=notes,
        patient_name=patient_name,
        patient_phone=patient_phone
    )
    return jsonify(result), 200


def _read_ledger_records():
    """Reads all appointment records safely from the CSV ledger."""
    ledger_path = os.path.join(os.path.dirname(__file__), "appointments_ledger.csv")
    if not os.path.exists(ledger_path):
        return []
    try:
        import csv
        with open(ledger_path, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception as ex:
        print(f"  ⚠️ [CSV Read Warning]: {ex}")
        return []


@app.route("/api/v1/appointments", methods=["GET"])
def list_appointments_api():
    """Returns Booked Appointments from Master CSV Ledger."""
    records = _read_ledger_records()
    return jsonify({
        "status": "SUCCESS",
        "count": len(records),
        "appointments": records
    }), 200


@app.route("/api/v1/appointments/lock", methods=["POST"])
def lock_slot_api():
    """Acquires a 10-Minute Ephemeral Mutex Slot Hold."""
    data = request.get_json(force=True, silent=True) or {}
    slot = data.get("slot", "")
    patient_phone = data.get("phone", "")

    if not slot or not patient_phone:
        return jsonify({"status": "ERROR", "message": "Fields 'slot' and 'phone' are required."}), 400

    lock_mgr = core_engine.lock_mgr
    lock_result = lock_mgr.acquire_slot_lock(slot, patient_phone)

    return jsonify({
        "status": "SUCCESS" if lock_result.get("status") == "LOCK_ACQUIRED" else "LOCK_DENIED",
        "lock_data": lock_result
    }), 200


@app.route("/api/v1/telemetry", methods=["GET"])
def telemetry_api():
    """Real-Time Analytics & System Telemetry API."""
    records = _read_ledger_records()
    total_leads = len(records)
    vip_count = sum(1 for r in records if "VIP" in str(r.get("lead_tier", "")))
    emergency_count = sum(1 for r in records if "EMERGENCY" in str(r.get("lead_tier", "")))

    return jsonify({
        "status": "SUCCESS",
        "telemetry": {
            "total_leads_processed": total_leads,
            "vip_leads_count": vip_count,
            "emergency_leads_count": emergency_count,
            "deduplicated_sids_active": len(processed_sids),
            "uptime_seconds": round(time.time() - start_timestamp, 2)
        }
    }), 200


def start_flask_server(host: str = "0.0.0.0", port: int = None):
    """Starts the Flask server on specified host and port (Defaults to $PORT env var)."""
    if port is None:
        port = int(os.getenv("PORT", 5000))
    print(f"\n=======================================================")
    print(f" 🛡️ CENTAUR OS UNBREAKABLE FLASK BACKEND RUNNING ")
    print(f" 📍 Port Bounded     : {port} (0.0.0.0)")
    print(f" 📍 Webhook Endpoint : http://{host}:{port}/webhook/whatsapp")
    print(f" 📍 Health Endpoint  : http://{host}:{port}/")
    print(f" 📍 Intake API       : http://{host}:{port}/api/v1/intake")
    print(f"=======================================================\n")
    app.run(host=host, port=port, threaded=True, debug=False)


if __name__ == "__main__":
    start_flask_server()
