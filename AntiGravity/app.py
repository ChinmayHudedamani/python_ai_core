# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX Dental Center AI Concierge — Yelahanka Node v0.2 Main Entry Point

import sys
from pathlib import Path

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import and execute main Streamlit UI from app/ui/demo_app.py
from app.ui.demo_app import *
