import sys
import os
from pathlib import Path

# Insert month1_python_core to Python System Path
sys.path.insert(0, str(Path(__file__).parent / "month1_python_core"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from flask_backend_server import start_flask_server

if __name__ == "__main__":
    print("\n==================================================")
    print(" 🚀 CENTAUR CLINIC ENTERPRISE FLASK PRODUCTION OS")
    print(" 👨‍💻 Powered by Google Gemini 2.0 Flash + Flask REST Backend")
    print("==================================================\n")
    start_flask_server(host="0.0.0.0", port=5000)
