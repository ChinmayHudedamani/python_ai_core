import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from twilio_config import save_twilio_credentials, load_twilio_credentials

if __name__ == "__main__":
    print("==================================================")
    print(" 🔑 TWILIO SANDBOX CREDENTIALS SETUP WIZARD")
    print("==================================================\n")

    current = load_twilio_credentials()
    print(f"Current Account SID : {current.get('account_sid')}")
    print(f"Current Auth Token  : {'*' * 8 if current.get('auth_token') else 'Not Set'}\n")

    sid = input("Enter your Twilio Account SID (starts with AC...): ").strip()
    token = input("Enter your Twilio Auth Token: ").strip()
    number = input("Enter Twilio Sandbox WhatsApp Number [Default: whatsapp:+14155238886]: ").strip() or "whatsapp:+14155238886"

    if sid and token:
        save_twilio_credentials(sid, token, number)
        print("\n✅ Twilio Credentials Updated and Saved in twilio_credentials.json!")
    else:
        print("\n⚠️ Account SID and Auth Token cannot be empty.")
