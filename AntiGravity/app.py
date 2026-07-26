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

# Start 6:00 AM Daily WhatsApp PDF Dispatcher for Dr. Chinmay Hudedamani
try:
    from daily_cron_scheduler import start_automated_6am_scheduler
    start_automated_6am_scheduler(doctor_phone="+91-7338350871")
except Exception as ex:
    print(f"Daily 6AM Scheduler Initialization Error: {ex}")

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


from core.meta_whatsapp import MetaWhatsAppCloudEngine

meta_engine = MetaWhatsAppCloudEngine()


@app.route("/webhook/meta", methods=["GET", "POST"])
def meta_whatsapp_webhook():
    """Official Meta WhatsApp Cloud API Webhook Handler."""
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == meta_engine.verify_token:
            return Response(challenge, status=200, mimetype="text/plain")
        return Response("Verification failed", status=403)

    try:
        body = request.get_json(force=True, silent=True) or {}
        entries = body.get("entry", [])
        if entries:
            changes = entries[0].get("changes", [])
            if changes:
                value = changes[0].get("value", {})
                messages = value.get("messages", [])
                if messages:
                    msg = messages[0]
                    from_phone = msg.get("from", "")
                    body_text = msg.get("text", {}).get("body", "").strip()
                    contacts = value.get("contacts", [])
                    name = contacts[0].get("profile", {}).get("name", "Patient") if contacts else "Patient"

                    if body_text and from_phone:
                        res = core_engine.process_patient_intake(
                            raw_notes=body_text,
                            patient_name=name,
                            patient_phone=from_phone,
                            send_dispatch=False
                        )
                        reply = res.get("whatsapp_response", "")
                        meta_engine.send_whatsapp_message(from_phone, reply)
    except Exception as ex:
        print(f"  🚨 [META WEBHOOK EXCEPTION]: {ex}")

    return Response("EVENT_RECEIVED", status=200, mimetype="text/plain")


@app.route("/demo", methods=["GET"])
def whatsapp_simulator():
    return render_template("whatsapp_demo.html")


@app.route("/pay/<slot_id>", methods=["GET"])
def payment_checkout_page(slot_id):
    return render_template("payment_gateway.html", slot_id=slot_id)


import hmac
import hashlib

RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "centaur_razorpay_secret_2026")


@app.route("/api/v1/razorpay_webhook", methods=["POST"])
def razorpay_webhook_authenticated():
    """Cryptographically validated Razorpay Payment Webhook Handler."""
    received_signature = request.headers.get("X-Razorpay-Signature", "")
    raw_payload = request.get_data()

    if not received_signature:
        return jsonify({"status": "FORBIDDEN", "message": "Missing X-Razorpay-Signature header."}), 403

    expected_signature = hmac.new(
        key=RAZORPAY_WEBHOOK_SECRET.encode("utf-8"),
        msg=raw_payload,
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, received_signature):
        return jsonify({"status": "FORBIDDEN", "message": "HMAC signature verification failed."}), 403

    payload = request.get_json(force=True, silent=True) or {}
    event = payload.get("event")

    if event in ["payment.captured", "payment.authorized"]:
        entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        txn_id = entity.get("id", f"TXN_RZP_{int(time.time())}")
        notes = entity.get("notes", {})
        patient_phone = notes.get("phone", "+91-9988776655")
        patient_name = notes.get("name", "Valued Patient")
        slot_id = notes.get("slot_id", "SLOT_GENERAL")

        ledger_res = ledger_writer.write_appointment_lead(
            name=patient_name,
            phone=patient_phone,
            procedure_code="GENERAL",
            raw_notes=f"Confirmed Paid Appointment (Slot {slot_id})",
            payment_status="PAID_CONFIRMED",
            transaction_id=txn_id
        )
        return jsonify({"status": "SUCCESS", "event": event, "ledger_result": ledger_res}), 200

    return jsonify({"status": "IGNORED_EVENT", "event": event}), 200


@app.route("/api/v1/pay_confirm", methods=["POST"])
def payment_confirm_api():
    # Enforce token header validation for legacy checkout endpoint
    auth_header = request.headers.get("Authorization", "")
    expected_secret = os.getenv("API_SECRET_KEY", "centaur_api_secret_2026")
    if not auth_header or expected_secret not in auth_header:
        return jsonify({"status": "UNAUTHORIZED", "message": "Valid API secret key required."}), 401

    data = request.get_json(force=True, silent=True) or {}
    slot_id = data.get("slot_id", "SLOT_GENERAL")
    txn_id = data.get("transaction_id", f"TXN_{int(time.time())}")
    phone = data.get("phone", "+91-9988776655")
    name = data.get("name", "Patient")

    ledger_res = ledger_writer.write_appointment_lead(
        name=name,
        phone=phone,
        procedure_code="GENERAL",
        raw_notes=f"Confirmed Paid Appointment (Slot {slot_id})",
        payment_status="PAID_CONFIRMED",
        transaction_id=txn_id
    )
    return jsonify({
        "status": "SUCCESS",
        "slot_id": slot_id,
        "transaction_id": txn_id,
        "ledger_result": ledger_res
    }), 200


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


@app.route("/download/doctor_report.pdf", methods=["GET"])
def download_doctor_pdf():
    from generate_doctor_pdf_report import build_doctor_pdf_report
    pdf_path = build_doctor_pdf_report("Apex_Dental_Doctor_Report.pdf")
    from flask import send_file
    return send_file(pdf_path, as_attachment=True, download_name="Apex_Dental_Doctor_Report.pdf")


@app.route("/api/v1/send_doctor_pdf", methods=["POST", "GET"])
def dispatch_doctor_pdf_api():
    from send_pdf_to_doctor import send_pdf_report_to_doctor
    phone = request.args.get("phone") or (request.get_json(force=True, silent=True) or {}).get("phone", os.getenv("DOCTOR_PHONE", "+91-7338350871"))
    return jsonify(res), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True, debug=False)
