import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from day2_python import mask_pii

CONVERSATIONS_DIR: Path = Path(__file__).parent / "conversations"
MASTER_HISTORY_FILE: Path = Path(__file__).parent / "conversations" / "conversations_master.json"
MAX_ALLOWED_TURNS: int = 8  # Safety circuit limit: > 8 follow-ups triggers Receptionist Handoff


def ensure_conversations_directory() -> None:
    """Ensures local conversation storage directory exists."""
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)


class ConversationSessionStore:
    """
    Multi-Turn Conversation Transcript Store & Human Handoff Circuit Breaker.
    - Limits automated AI follow-ups to MAX_ALLOWED_TURNS (8 turns).
    - If > 8 questions asked, flags status as RECEPTIONIST_REQUIRED, provides front desk contact info,
      and freezes further automated storage to prevent infinite conversation loops.
    """

    def __init__(self, max_turns: int = MAX_ALLOWED_TURNS):
        ensure_conversations_directory()
        self.max_turns: int = max_turns
        self.master_path: Path = MASTER_HISTORY_FILE
        self._ensure_master_file_initialized()

    def _ensure_master_file_initialized(self) -> None:
        """Initializes master conversation archive file if missing."""
        if not self.master_path.exists():
            with open(self.master_path, "w", encoding="utf-8") as f:
                json.dump({"total_sessions": 0, "sessions": []}, f, indent=2)

    def get_session_file_path(self, phone: str) -> Path:
        """Derives clean file path for patient conversation transcript."""
        clean_phone: str = phone.replace("-", "").replace(" ", "").replace("+", "")
        return CONVERSATIONS_DIR / f"chat_{clean_phone}.json"

    def load_patient_session(self, phone: str) -> Dict[str, Any]:
        """Loads active multi-turn session or initializes a new transcript structure."""
        file_path: Path = self.get_session_file_path(phone)
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "phone": phone,
            "masked_phone": mask_pii(phone),
            "session_created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "ACTIVE_AUTOMATED",
            "total_turns": 0,
            "turns": []
        }

    def check_turn_limit_exceeded(self, phone: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluates whether patient session has exceeded the 8 follow-up turn threshold.
        If > 8 turns, flags status as RECEPTIONIST_REQUIRED and returns handoff payload.
        """
        session: Dict[str, Any] = self.load_patient_session(phone)
        current_turns: int = session.get("total_turns", 0)

        if current_turns >= self.max_turns or session.get("status") == "RECEPTIONIST_REQUIRED":
            # Flag session as RECEPTIONIST_REQUIRED
            session["status"] = "RECEPTIONIST_REQUIRED"
            session["flagged_reason"] = f"Exceeded maximum automated turn limit ({self.max_turns} follow-ups)"
            session["last_updated_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

            session_file: Path = self.get_session_file_path(phone)
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session, f, indent=2)

            self._update_master_index(session)

            handoff_response = (
                "📞 **HUMAN RECEPTIONIST HANDOFF REQUIRED** 📞\n\n"
                "You have reached the maximum automated follow-up question limit (8 follow-ups).\n"
                "To ensure you receive exact personalized clinical care, your query has been flagged for our Senior Receptionist.\n\n"
                "📍 **Front Desk Direct Contact**: +91-9988776655\n"
                "🕒 **Reception Hours**: 9:00 AM - 8:00 PM (Monday - Saturday)\n"
                "💬 Reply 'CALL ME' to request an immediate callback from our staff."
            )

            return True, {
                "status": "RECEPTIONIST_REQUIRED_LIMIT_EXCEEDED",
                "total_turns": current_turns,
                "max_turns": self.max_turns,
                "whatsapp_response": handoff_response,
                "circuit_action": "BOT_FAILURE_HANDOFF_TO_RECEPTIONIST",
                "session_file": str(session_file)
            }

        return False, {}

    def append_chat_turn(self, phone: str, user_message: str, bot_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Appends a user query and bot response pair to the patient's persistent conversation file.
        If max turn limit is reached, freezes further AI storage and flags RECEPTIONIST_REQUIRED.
        """
        exceeded, handoff_data = self.check_turn_limit_exceeded(phone)
        if exceeded:
            return handoff_data

        session: Dict[str, Any] = self.load_patient_session(phone)
        turn_id: int = session["total_turns"] + 1

        triage = bot_response.get("triage", {})
        grounding = bot_response.get("grounding_facts", {})
        circuit = bot_response.get("circuit_status", {})

        turn_payload: Dict[str, Any] = {
            "turn_index": turn_id,
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "user_query": user_message,
            "bot_reply": bot_response.get("whatsapp_response", ""),
            "triage_tier": triage.get("lead_tier", "COLD_ROUTINE"),
            "intent_score": triage.get("intent_score", 0),
            "citations": grounding.get("citations", []),
            "circuit_action": circuit.get("circuit_action", "STANDARD_AUTOMATED_REPLY")
        }

        session["turns"].append(turn_payload)
        session["total_turns"] = len(session["turns"])
        session["last_updated_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if session["total_turns"] >= self.max_turns:
            session["status"] = "RECEPTIONIST_REQUIRED"
            session["flagged_reason"] = f"Reached turn limit ({self.max_turns} follow-ups)"

        # Save Patient Transcript File
        session_file: Path = self.get_session_file_path(phone)
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2)

        # Update Master Index
        self._update_master_index(session)

        return {
            "status": "CONVERSATION_SAVED" if session["total_turns"] < self.max_turns else "RECEPTIONIST_REQUIRED_LIMIT_REACHED",
            "session_file": str(session_file),
            "turn_index": turn_id,
            "total_turns": session["total_turns"],
            "max_turns": self.max_turns
        }

    def _update_master_index(self, session: Dict[str, Any]) -> None:
        """Appends or updates session reference in master index file."""
        try:
            with open(self.master_path, "r", encoding="utf-8") as f:
                master_data = json.load(f)

            phone = session["phone"]
            existing = [s for s in master_data.get("sessions", []) if s.get("phone") == phone]
            if existing:
                existing[0]["total_turns"] = session["total_turns"]
                existing[0]["status"] = session.get("status", "ACTIVE_AUTOMATED")
                existing[0]["last_updated_utc"] = session["last_updated_utc"]
            else:
                master_data["sessions"].append({
                    "phone": phone,
                    "masked_phone": mask_pii(phone),
                    "status": session.get("status", "ACTIVE_AUTOMATED"),
                    "session_file": str(self.get_session_file_path(phone)),
                    "total_turns": session["total_turns"],
                    "last_updated_utc": session["last_updated_utc"]
                })

            master_data["total_sessions"] = len(master_data["sessions"])
            with open(self.master_path, "w", encoding="utf-8") as f:
                json.dump(master_data, f, indent=2)
        except Exception:
            pass


if __name__ == "__main__":
    store = ConversationSessionStore(max_turns=8)
    print(f"Initialized conversation store with MAX_TURNS={store.max_turns}")
