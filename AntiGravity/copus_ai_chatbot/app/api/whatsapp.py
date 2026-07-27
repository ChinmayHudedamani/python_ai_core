"""Meta WhatsApp Cloud API Ingress & Webhook Verification Router."""

import logging
from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse

from app.core.config import settings
from app.core.guardrails import sanitize_input
from app.services.triage_engine import TriageEngine
from app.services.llm_router import get_agent_context, is_authorized_doctor

logger = logging.getLogger("APEX_AI_WHATSAPP_API")

router = APIRouter(prefix="/webhooks/whatsapp", tags=["WhatsApp"])


@router.get("")
async def verify_whatsapp_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """Meta Webhook Challenge Verification Endpoint."""
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("Meta WhatsApp Webhook verification successful.")
        return PlainTextResponse(content=hub_challenge, status_code=200)

    logger.warning("Meta WhatsApp Webhook verification failed. Invalid token.")
    raise HTTPException(status_code=403, detail="Verification token mismatch.")


@router.post("")
async def receive_whatsapp_message(request: Request):
    """Ingress handler for live inbound WhatsApp patient & doctor messages."""
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    entries = payload.get("entry", [])
    if not entries:
        return JSONResponse(status_code=200, content={"status": "ignored", "reason": "empty entry"})

    for entry in entries:
        for change in entry.get("changes", []):
            value = change.get("value", {})
            if "statuses" in value and "messages" not in value:
                continue

            messages = value.get("messages", [])
            for message in messages:
                from_phone = message.get("from", "")
                text_body = message.get("text", {}).get("body", "").strip()

                if not from_phone or not text_body:
                    continue

                sanitized = sanitize_input(text_body)
                if sanitized.get("is_flagged"):
                    logger.warning(f"Message from {from_phone} flagged by Pre-Guardrails.")
                    continue

                triage_engine = TriageEngine()
                triage_res = triage_engine.evaluate_message(text_body)
                if triage_res:
                    logger.critical(f"EMERGENCY TRIAGE ALERT for {from_phone}: {triage_res['matched_keyword']}")
                    continue

                prompt, registry, role = get_agent_context(from_phone)
                logger.info(f"Routed message from {from_phone} to Agent Role '{role}'.")

    return JSONResponse(status_code=200, content={"status": "processed"})
