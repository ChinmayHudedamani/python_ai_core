# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Official Meta WhatsApp Cloud API Ingress Webhook

import os
import json
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException, Query, Depends
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.services.whatsapp_client import WhatsAppClient
from app.services.guardrails import sanitize_input
from app.services.triage_engine import TriageEngine
from app.services.llm_router import get_agent_context

logger = logging.getLogger("APEX_AI_WHATSAPP_INGRESS")

router = APIRouter(prefix="/webhooks", tags=["WhatsApp Ingress"])

WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "apex_ai_secure_verify_token_2026")


@router.get("/whatsapp")
async def verify_whatsapp_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge")
):
    """Meta Webhook Verification Endpoint (GET). Returns raw hub.challenge on token match."""
    logger.info(f"🔍 Meta Webhook Verification request received: mode={hub_mode}")

    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        if hub_challenge is not None:
            logger.info("✅ Meta Webhook Verification successful!")
            return PlainTextResponse(content=hub_challenge, status_code=200)

    logger.warning("❌ Meta Webhook Verification failed: Token mismatch or invalid mode.")
    raise HTTPException(status_code=403, detail="Verification token mismatch")


@router.post("/whatsapp")
async def whatsapp_message_ingress(
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """Meta Inbound Message Webhook (POST). Consumes live WhatsApp messages and dispatches responses."""
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Extract Meta message components
    entries = payload.get("entry", [])
    if not entries:
        return JSONResponse(status_code=200, content={"status": "ignored_empty_entry"})

    changes = entries[0].get("changes", [])
    if not changes:
        return JSONResponse(status_code=200, content={"status": "ignored_no_changes"})

    value = changes[0].get("value", {})
    messages = value.get("messages", [])

    # Filter out read/delivered receipt status updates
    if not messages:
        logger.info("ℹ️ Status update (read/delivered receipt) received and safely ignored.")
        return JSONResponse(status_code=200, content={"status": "ignored_status_update"})

    msg_obj = messages[0]
    from_phone = msg_obj.get("from", "")
    msg_type = msg_obj.get("type", "")

    # Only process text messages
    if msg_type != "text":
        logger.info(f"Non-text message type '{msg_type}' received from {from_phone}.")
        client = WhatsAppClient()
        await client.send_text_message(
            to_phone=from_phone,
            message="Thank you for your message! Currently, I am optimized for text responses. How can I assist you with your dental care today?"
        )
        return JSONResponse(status_code=200, content={"status": "non_text_processed"})

    raw_text = msg_obj.get("text", {}).get("body", "")
    logger.info(f"💬 Live WhatsApp Message from {from_phone}: '{raw_text}'")

    # 1. Pre-Guardrail Sanitization
    sanitized = sanitize_input(raw_text)
    if sanitized.get("is_flagged"):
        logger.warning(f"🚨 Prompt injection attempt flagged from {from_phone}!")
        client = WhatsAppClient()
        await client.send_text_message(
            to_phone=from_phone,
            message="I am trained to assist with clinical appointments and dental inquiries. How can I help you today?"
        )
        return JSONResponse(status_code=200, content={"status": "injection_flagged"})

    # 2. Multilingual Emergency Triage Check
    triage_engine = TriageEngine()
    triage_result = triage_engine.evaluate_message(raw_text)

    client = WhatsAppClient()

    if triage_result:
        urgency = triage_result["urgency_level"]
        instructions = triage_result["first_aid_instructions"]
        logger.info(f"🚨 Triage Emergency Triggered ({urgency}) for {from_phone}")

        if urgency == "CRITICAL_EMERGENCY":
            emergency_reply = (
                f"🚨 URGENT MEDICAL ALERT: {instructions}\n\n"
                f"Please call our emergency line immediately at +91-9988776655."
            )
        else:
            emergency_reply = (
                f"⚠️ Urgent Dental Concern: {instructions}\n\n"
                f"Would you like me to find you an immediate slot with Dr. Chinmay Hudedamani?"
            )

        await client.send_text_message(to_phone=from_phone, message=emergency_reply)
        return JSONResponse(status_code=200, content={"status": "triage_emergency_dispatched"})

    # 3. RBAC Persona Router & Agent Response
    system_prompt, bound_registry, role = get_agent_context(from_phone)

    if role == "DOCTOR_EXECUTIVE_ASSISTANT":
        reply = f"🤖 APEX Executive Doctor Assistant: Ready to report. Ask for daily ledgers or revenue summaries."
    else:
        reply = (
            f"Hello! 👋 I'm APEX AI from Apex Dental Center & Implant Institute.\n\n"
            f"How can I help you today? Please tell me your primary symptom or health concern so I can guide you!"
        )

    await client.send_text_message(to_phone=from_phone, message=reply)

    return JSONResponse(status_code=200, content={"status": "success", "agent_role": role})
