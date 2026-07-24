import os
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR: Path = Path(__file__).parent
ENV_FILE: Path = BASE_DIR / ".env"
CONFIG_FILE: Path = BASE_DIR / "system_config.json"

DEFAULT_SYSTEM_CONFIG: Dict[str, Any] = {
    "clinic_name": "Apex Dental Center & Implant Institute",
    "chief_doctor_name": "Dr. Chinmay Hudedamani",
    "doctor_phone": "+91-9988776655",
    "clinic_address": "100 Feet Road, 4th Block, Koramangala, Bengaluru, Karnataka 560034",
    "currency_symbol": "₹",
    "max_allowed_followup_turns": 8,
    "slot_reservation_ttl_seconds": 600,
    "rate_limit_max_requests_per_min": 5,
    "meta_verify_token": "apex_centaur_meta_verify_token_2026",
    "meta_app_secret": "apex_dental_centaur_secret_key_2026",
    "twilio": {
        "account_sid": os.getenv("TWILIO_ACCOUNT_SID", "AC_TWILIO_DEMO_ACCOUNT_SID"),
        "auth_token": os.getenv("TWILIO_AUTH_TOKEN", "TWILIO_DEMO_AUTH_TOKEN"),
        "sandbox_whatsapp_number": "whatsapp:+14155238886",
        "webhook_port": 5000
    }
}


class SystemConfigManager:
    """
    Singleton Configuration Manager for Centaur OS.
    Centralizes system environment variables, credentials, and clinic business settings.
    """
    _instance: Optional['SystemConfigManager'] = None

    def __new__(cls) -> 'SystemConfigManager':
        if cls._instance is None:
            cls._instance = super(SystemConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        self.config: Dict[str, Any] = DEFAULT_SYSTEM_CONFIG.copy()
        self.load_config_file()

    def load_config_file(self) -> None:
        """Loads configuration overrides from system_config.json if present."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
            except Exception as e:
                print(f"⚠️ Error loading system_config.json: {e}")
        else:
            self.save_config_file()

    def save_config_file(self) -> None:
        """Persists current system configuration to JSON file."""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving system_config.json: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a configuration parameter by key."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Updates a configuration parameter and persists changes."""
        self.config[key] = value
        self.save_config_file()


if __name__ == "__main__":
    cfg = SystemConfigManager()
    print("  ✅ System Configuration Manager Initialized:")
    print(json.dumps(cfg.config, indent=2))
