import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from day2_python import mask_pii

CONVERSATIONS_DIR: Path = Path(__file__).parent / "conversations"
MASTER_HISTORY_FILE: Path = Path(__file__).parent / "conversations" / "conversations_master.json"

def ensure_conversations_directory() -> None:
    """Ensures local conversation storage directory exists."""
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)


class ConversationSessionStore:
    """
    Multi-Turn Conversation Transcript Store & Audit Ledger.
    Maintains persistent multi-turn chat histories per patient phone number
    and archives complete turn-by-turn conversation JSON logs for future analysis.
    """

    def __init__(self):
        ensure_conversations_directory()
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
            "total_turns": 0,
            "turns": []
        }

    def append_chat_turn(self, phone: str, user_message: str, bot_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Appends a user query and bot response pair to the patient's persistent conversation file.
        Updates master history archive.
        """
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

        # Save Patient Transcript File
        session_file: Path = self.get_session_file_path(phone)
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2)

        # Update Master Index
        self._update_master_index(session)

        return {
            "status": "CONVERSATION_SAVED",
            "session_file": str(session_file),
            "turn_index": turn_id
        }

    def _update_master_index(self, session: Dict[str, Any]) -> None:
        """Appends session reference to master index file."""
        try:
            with open(self.master_path, "r", encoding="utf-8") as f:
                master_data = json.load(f)

            phone = session["phone"]
            existing = [s for s in master_data.get("sessions", []) if s.get("phone") == phone]
            if existing:
                existing[0]["total_turns"] = session["total_turns"]
                existing[0]["last_updated_utc"] = session["last_updated_utc"]
            else:
                master_data["sessions"].append({
                    "phone": phone,
                    "masked_phone": mask_pii(phone),
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
    store = ConversationSessionStore()
    print(f"Initialized conversation store at: {store.master_path}")
