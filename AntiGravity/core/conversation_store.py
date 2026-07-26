import os
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple

CONVERSATIONS_DIR = Path(__file__).parent.parent / "conversations"


def ensure_conversations_directory():
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)


class ConversationSessionStore:
    """Multi-Turn Conversation Transcript Store & Human Handoff Circuit Breaker."""

    def __init__(self, max_turns: int = 8):
        ensure_conversations_directory()
        self.max_turns = max_turns

    def get_session_file_path(self, phone: str) -> Path:
        clean_phone = phone.replace("-", "").replace(" ", "").replace("+", "")
        return CONVERSATIONS_DIR / f"chat_{clean_phone}.json"

    def load_patient_session(self, phone: str) -> Dict[str, Any]:
        file_path = self.get_session_file_path(phone)
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "phone": phone,
            "session_created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "ACTIVE_AUTOMATED",
            "total_turns": 0,
            "turns": []
        }

    def reset_session(self, phone: str) -> None:
        """Resets session turn counter and clears RECEPTIONIST_REQUIRED status."""
        session_file = self.get_session_file_path(phone)
        session = self.load_patient_session(phone)
        session["status"] = "ACTIVE_AUTOMATED"
        session["total_turns"] = 0
        session["turns"] = []
        session["last_updated_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session, f, indent=2)
        except Exception:
            pass

    def check_turn_limit_exceeded(self, phone: str, user_message: str = "") -> Tuple[bool, Dict[str, Any]]:
        """Evaluates turn limit and auto-resets session on greeting / reset intent / 30-min timeout."""
        clean_msg = user_message.strip().lower()
        if clean_msg in ["hi", "hello", "hey", "start over", "reset", "start", "1", "yes", "confirm"]:
            self.reset_session(phone)
            return False, {}

        session = self.load_patient_session(phone)
        current_turns = session.get("total_turns", 0)

        # Check 30 min timeout
        last_updated_str = session.get("last_updated_utc")
        if last_updated_str:
            try:
                last_updated = datetime.datetime.fromisoformat(last_updated_str)
                now = datetime.datetime.now(datetime.timezone.utc)
                if (now - last_updated).total_seconds() > 1800:
                    self.reset_session(phone)
                    return False, {}
            except Exception:
                pass

        if current_turns >= self.max_turns or session.get("status") == "RECEPTIONIST_REQUIRED":
            session["status"] = "RECEPTIONIST_REQUIRED"
            session["last_updated_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            session_file = self.get_session_file_path(phone)
            try:
                with open(session_file, "w", encoding="utf-8") as f:
                    json.dump(session, f, indent=2)
            except Exception:
                pass

            handoff_response = (
                "📞 Senior Receptionist Handoff\n\n"
                "You have reached the maximum automated follow-up question limit.\n"
                "To ensure you receive exact personalized clinical care, your query has been flagged for our Senior Receptionist.\n\n"
                "📍 Direct Contact: +91-9988776655\n"
                "🕒 Operating Hours: 9:00 AM - 8:00 PM (Monday - Saturday)"
            )
            return True, {
                "status": "RECEPTIONIST_REQUIRED_LIMIT_EXCEEDED",
                "whatsapp_response": handoff_response
            }

        return False, {}

    def append_chat_turn(self, phone: str, user_message: str, bot_response: Dict[str, Any]) -> None:
        session = self.load_patient_session(phone)
        turn_id = session["total_turns"] + 1

        turn_payload = {
            "turn_index": turn_id,
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "user_query": user_message,
            "bot_reply": bot_response.get("whatsapp_response", "")
        }

        session["turns"].append(turn_payload)
        session["total_turns"] = len(session["turns"])
        session["last_updated_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

        session_file = self.get_session_file_path(phone)
        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session, f, indent=2)
        except Exception:
            pass
