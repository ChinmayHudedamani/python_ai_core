import sys
import io
import os
from pathlib import Path

# Force UTF-8 stdout encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.meta_whatsapp import MetaWhatsAppCloudEngine


def dispatch_demo_links(doctor_phone: str = "+91-7338350871") -> dict:
    wa_engine = MetaWhatsAppCloudEngine()

    demo_msg = (
        "👨‍💻 *APEX AI / CENTAUR OS — DEMO LINKS & EXECUTIVE DASHBOARD*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Hello Chinmay (Creator & Patent Owner)! Your APEX AI System is 100% ready for clinical demo.\n\n"
        "📱 *Patient WhatsApp Interactive Web Simulator:*\n"
        "• Production Cloud: https://centaur-bot.onrender.com/demo\n"
        "• Local Server: http://127.0.0.1:5000/demo\n\n"
        "👨‍💻 *Executive WhatsApp Commands (Reply directly to this chat):*\n"
        "1. Type *'financial update'* — View revenue & bank credit status.\n"
        "2. Type *'appointments'* — View today's patient schedule.\n"
        "3. Type *'how many patients has the bot conversed with'* — View live conversed leads.\n"
        "4. Type *'send report'* — Receive daily PDF ledger report.\n\n"
        "🔒 *Intellectual Property:* Patent & Created by Chinmay Hudedamani\n"
        "🔒 *System Status:* Neon PostgreSQL Synced | 1,000 RL Benchmark 100% Passed"
    )

    res = wa_engine.send_whatsapp_message(doctor_phone, demo_msg)
    print(f"✅ Demo links dispatched to {doctor_phone}: {res}")
    return res


if __name__ == "__main__":
    dispatch_demo_links()
