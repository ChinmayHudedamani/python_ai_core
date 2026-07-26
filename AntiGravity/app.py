import os
import sys
import time
import threading
from flask import Flask, request, Response, jsonify, render_template
from flask_cors import CORS

# Add root directory to Python System Path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.engine import CentaurCoreEngine
from clinical.ledger_writer import OfflineLedgerWriter

# Initialize Flask App
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Singletons
core_engine = CentaurCoreEngine()
ledger_writer = OfflineLedgerWriter()

processed_sids_file = os.path.join(current_dir, "processed_sids.txt")
processed_sids = set()
if os.path.exists(processed_sids_file):
    try:
        with open(processed_sids_file, "r", encoding="utf-8") as sf:
            processed_sids = set(line.strip() for line in sf if line.strip())
    except Exception:
        pass
sid_lock = threading.Lock()
start_timestamp = time.time()


@app.errorhandler(Exception)
def handle_global_exception(e):
    error_msg = str(e)
    print(f"  🚨 [FAIL-SAFE RECOVERY]: {error_msg}")
    if request.path.startswith("/webhook/whatsapp"):
        return Response('<?xml version="1.0" encoding="UTF-8"?><Response></Response>', mimetype="text/xml")
    return jsonify({"status": "ERROR_RECOVERED", "error": error_msg, "timestamp": time.time()}), 200


@app.route("/demo", methods=["GET"])
def whatsapp_simulator():
    return render_template("whatsapp_demo.html")


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "HEALTHY",
        "system": "Centaur OS Enterprise Backend",
        "uptime_seconds": round(time.time() - start_timestamp, 2),
        "port": int(os.getenv("PORT", 5000))
    }), 200


@app.route("/webhook/whatsapp", methods=["POST", "GET"])
def whatsapp_webhook():
    if request.method == "GET":
        return Response('<?xml version="1.0" encoding="UTF-8"?><Response><Message>Centaur OS Webhook Online</Message></Response>', mimetype="text/xml")

    form_data = request.form
    msg_sid = form_data.get("MessageSid", "").strip()
    from_number = form_data.get("From", "").replace("whatsapp:", "").strip()
    body_text = form_data.get("Body", "").strip()
    profile_name = form_data.get("ProfileName", "Patient").strip()

    # 1. Ignore Twilio Status Callbacks (sent, delivered, read) & empty messages
    if form_data.get("MessageStatus") or form_data.get("SmsStatus") or not body_text:
        return Response('<?xml version="1.0" encoding="UTF-8"?><Response></Response>', mimetype="text/xml")

    # 2. Strict MessageSID Deduplication Hold
    if msg_sid:
        with sid_lock:
            if msg_sid in processed_sids:
                return Response('<?xml version="1.0" encoding="UTF-8"?><Response></Response>', mimetype="text/xml")
            processed_sids.add(msg_sid)
            try:
                with open(processed_sids_file, "a", encoding="utf-8") as sf:
                    sf.write(f"{msg_sid}\n")
            except Exception:
                pass

    # 3. Process Intake (send_dispatch=False so ZERO REST API CALLS ARE MADE)
    try:
        pipeline_result = core_engine.process_patient_intake(
            raw_notes=body_text,
            patient_name=profile_name,
            patient_phone=from_number,
            send_dispatch=False
        )
        reply_text = pipeline_result.get("whatsapp_response", "Thank you for contacting Apex Dental Center.")
    except Exception as ex:
        reply_text = f"Hello {profile_name},\n\nThank you for contacting Apex Dental Center.\nOur clinic is currently open from 9:00 AM to 8:00 PM in Koramangala.\nDoctor: Dr. Chinmay Hudedamani."

    # 4. Return EXACTLY ONE TwiML XML Message payload
    twiml_response = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply_text}</Message></Response>'
    return Response(twiml_response, mimetype="text/xml")


@app.route("/api/v1/intake", methods=["POST"])
def patient_intake_api():
    data = request.get_json(force=True, silent=True) or {}
    notes = data.get("notes", "")
    patient_name = data.get("name", "Patient")
    patient_phone = data.get("phone", "+91-9988776655")

    if not notes:
        return jsonify({"status": "ERROR", "message": "Field 'notes' is required."}), 400

    result = core_engine.process_patient_intake(
        raw_notes=notes,
        patient_name=patient_name,
        patient_phone=patient_phone,
        send_dispatch=False
    )
    return jsonify(result), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True, debug=False)
