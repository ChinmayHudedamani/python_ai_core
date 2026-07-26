import os
import sys
import logging
from pathlib import Path

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DDL_STATEMENTS = [
    """
    -- 1. Appointments Ledger Table
    CREATE TABLE IF NOT EXISTS appointments_ledger (
        id UUID PRIMARY KEY,
        patient_number VARCHAR(50) NOT NULL,
        time_slot VARCHAR(150) NOT NULL UNIQUE,
        procedure_type VARCHAR(100) NOT NULL,
        transaction_id VARCHAR(100) NOT NULL,
        sha256_hash VARCHAR(64) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    -- Indexes for appointments_ledger
    CREATE INDEX IF NOT EXISTS idx_appointments_ledger_patient ON appointments_ledger(patient_number);
    CREATE INDEX IF NOT EXISTS idx_appointments_ledger_created ON appointments_ledger(created_at DESC);
    """,
    """
    -- 2. Conversation Transcripts Store Table (Optional Persistent Chat Store)
    CREATE TABLE IF NOT EXISTS conversation_transcripts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        phone VARCHAR(50) NOT NULL UNIQUE,
        status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE_AUTOMATED',
        total_turns INT DEFAULT 0,
        turns_data JSONB DEFAULT '[]'::jsonb,
        last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    -- Index for conversation_transcripts
    CREATE INDEX IF NOT EXISTS idx_conversations_phone ON conversation_transcripts(phone);
    """,
    """
    -- 3. Telemetry & Analytics Events Table
    CREATE TABLE IF NOT EXISTS telemetry_events (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        event_name VARCHAR(100) NOT NULL,
        payload JSONB DEFAULT '{}'::jsonb,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    -- 4. DB-backed Atomic Slot Reservations Table (Multi-worker Race-Condition Protection)
    CREATE TABLE IF NOT EXISTS slot_reservations (
        slot_id VARCHAR(150) PRIMARY KEY,
        reserved_by VARCHAR(50) NOT NULL,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL
    );
    """
]


def setup_database(db_url: str = None) -> bool:
    if not db_url:
        db_url = os.getenv("DATABASE_URL", "")

    if not db_url:
        logger.error("DATABASE_URL environment variable is not set.")
        return False

    if not PSYCOPG2_AVAILABLE:
        logger.error("psycopg2 is not installed in the python environment.")
        return False

    logger.info("Connecting to Neon PostgreSQL database...")
    try:
        with psycopg2.connect(db_url) as conn:
            with conn.cursor() as cur:
                for statement in DDL_STATEMENTS:
                    cur.execute(statement)
            conn.commit()
        logger.info("Successfully created all database tables and indexes in Neon PostgreSQL!")
        return True
    except Exception as e:
        logger.error(f"Error executing DDL setup: {e}")
        return False


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("DATABASE_URL", "")
    if not url:
        print("\n[!] DATABASE_URL variable not detected in environment.")
        url = input("Enter your Neon DATABASE_URL: ").strip()

    if url:
        setup_database(url)
    else:
        print("Aborted setup.")
