import os
import json
from pathlib import Path
from typing import Dict, Any

CONFIG_FILE: Path = Path(__file__).parent / "twilio_credentials.json"

DEFAULT_CONFIG: Dict[str, str] = {
    "account_sid": "AC_TWILIO_DEMO_ACCOUNT_SID_KEY",
    "auth_token": "TWILIO_DEMO_AUTH_TOKEN_KEY",
    "sandbox_whatsapp_number": "whatsapp:+14155238886",
    "webhook_port": "5000"
}


def load_twilio_credentials() -> Dict[str, str]:
    """Loads Twilio credentials from JSON configuration file or environment variables."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Save default placeholder config if file missing
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)

    return DEFAULT_CONFIG


def save_twilio_credentials(account_sid: str, auth_token: str, sandbox_number: str = "whatsapp:+14155238886") -> None:
    """Saves user-provided Twilio Sandbox credentials."""
    config = {
        "account_sid": account_sid.strip(),
        "auth_token": auth_token.strip(),
        "sandbox_whatsapp_number": sandbox_number.strip() if sandbox_number.startswith("whatsapp:") else f"whatsapp:{sandbox_number.strip()}",
        "webhook_port": "5000"
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print("  ✅ Twilio Sandbox Credentials Saved Successfully!")


if __name__ == "__main__":
    creds = load_twilio_credentials()
    print(json.dumps(creds, indent=2))
