import os
import sys
import time
import threading
import traceback
from flask import Flask, request, Response, jsonify
from flask_cors import CORS

# Add current dir and parent dir to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
for d in [current_dir, parent_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from core_engine import CentaurCoreEngine
from day5_python import OfflineLedgerWriter

# Initialize Flask App
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Singletons
core_engine = CentaurCoreEngine()
ledger_writer = OfflineLedgerWriter()

processed_sids = set()
sid_lock = threading.Lock()
start_timestamp = time.time()


@app.errorhandler(Exception)
def handle_global_exception(e):
    error_msg = str(e)
    print(f"  🚨 [FAIL-SAFE RECOVERY]: {error_msg}")
    if request.path.startswith("/webhook/whatsapp"):
        return Response('<?xml version="1.0" encoding="UTF-8"?><Response></Response>', mimetype="text/xml")
    return jsonify({"status": "ERROR_RECOVERED", "error": error_msg, "timestamp": time.time()}), 200


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "HEALTHY",
        "system": "Centaur OS Production Backend",
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

    if not body_text:
        return Response('<?xml version="1.0" encoding="UTF-8"?><Response></Response>', mimetype="text/xml")

    if msg_sid:
        with sid_lock:
            if msg_sid in processed_sids:
                return Response('<?xml version="1.0" encoding="UTF-8"?><Response></Response>', mimetype="text/xml")
            processed_sids.add(msg_sid)

    try:
        pipeline_result = core_engine.process_patient_intake(
            raw_notes=body_text,
            patient_name=profile_name,
            patient_phone=from_number
        )
        reply_text = pipeline_result.get("whatsapp_response", "Thank you for contacting Apex Dental Center.")
    except Exception as ex:
        reply_text = f"Hello {profile_name},\n\nThank you for contacting Apex Dental Center.\nOur clinic is currently open from 9:00 AM to 8:00 PM in Koramangala.\nDoctor: Dr. Chinmay Hudedamani."

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
        patient_phone=patient_phone
    )
    return jsonify(result), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True, debug=False)
