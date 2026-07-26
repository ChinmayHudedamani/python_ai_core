import os
import sys
import time
import threading
import logging
import requests
from pathlib import Path

# Ensure root directory is in sys.path
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from clinical.ledger_writer import get_db_url

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RENDER_APP_URL = os.getenv("RENDER_EXTERNAL_URL", "https://centaur-bot.onrender.com")


def keep_render_backend_alive():
    """Background worker that pings the Render backend health endpoint every 9 minutes to prevent cold-starts."""
    logger.info(f"⚡ Keep-Alive Pinger started for {RENDER_APP_URL}/health")

    while True:
        try:
            time.sleep(540)  # 9 minutes
            health_url = f"{RENDER_APP_URL.rstrip('/')}/health"
            res = requests.get(health_url, timeout=(3.05, 5.0))
            logger.info(f"🟢 [KEEP-ALIVE PING]: {health_url} -> Status {res.status_code}")
        except Exception as ex:
            logger.warning(f"🟡 [KEEP-ALIVE PING EXCEPTION]: {ex}")


def keep_neon_postgres_alive():
    """Background worker that executes a lightweight query on Neon PostgreSQL every 4 minutes to keep compute active."""
    logger.info("⚡ Neon PostgreSQL Keep-Alive Daemon started")

    while True:
        try:
            time.sleep(240)  # 4 minutes
            db_url = get_db_url()
            if PSYCOPG2_AVAILABLE and db_url:
                with psycopg2.connect(db_url, connect_timeout=3, options="-c statement_timeout=2000") as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1;")
                logger.info("🟢 [NEON DB KEEP-ALIVE]: PostgreSQL connection active & warm.")
        except Exception as ex:
            logger.warning(f"🟡 [NEON DB KEEP-ALIVE EXCEPTION]: {ex}")


def start_always_active_daemons():
    """Launches non-blocking background threads to ensure 24/7 backend and database uptime."""
    t1 = threading.Thread(target=keep_render_backend_alive, daemon=True)
    t2 = threading.Thread(target=keep_neon_postgres_alive, daemon=True)
    t1.start()
    t2.start()
    logger.info("✅ 24/7 Always-Active Uptime Daemons initialized (Render App + Neon PostgreSQL).")


if __name__ == "__main__":
    print("Testing 24/7 Keep-Alive Uptime Daemons...")
    start_always_active_daemons()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Daemon stopped.")
