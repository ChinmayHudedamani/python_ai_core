# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Zero-Trust Razorpay Webhook Endpoint & Idempotency Lock

import os
import json
import secrets
import uuid
import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.redis_client import get_redis_client
from app.services.payment import RazorpayAdapter
from app.models.booking import Booking, BookingStatus
from app.models.slot import Slot, SlotStatus
from app.models.audit_log import AuditLog

logger = logging.getLogger("APEX_AI_WEBHOOKS")

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "mock_razorpay_secret_123")


@router.post("/razorpay")
async def razorpay_webhook_handler(
    request: Request,
    x_razorpay_signature: str = Header(None, alias="x-razorpay-signature"),
    db: AsyncSession = Depends(get_async_db),
    redis = Depends(get_redis_client)
):
    """Zero-Trust Webhook Consumer: Cryptographically verifies signature and updates booking status idempotently."""
    body_bytes = await request.body()

    # 1. Cryptographic HMAC Signature Validation
    adapter = RazorpayAdapter()
    if not x_razorpay_signature or not adapter.verify_signature(body_bytes, x_razorpay_signature, RAZORPAY_WEBHOOK_SECRET):
        logger.warning("❌ Invalid or missing Razorpay Webhook Signature.")
        raise HTTPException(status_code=401, detail="Invalid Razorpay Webhook Signature")

    # 2. Parse Webhook Event Payload
    try:
        event = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON Payload")

    # Support standard Razorpay payload structure and direct mock payloads
    payment_entity = event.get("payload", {}).get("payment", {}).get("entity", {})
    payment_id = payment_entity.get("id") or event.get("payment_id")
    booking_id_str = (
        payment_entity.get("notes", {}).get("booking_id")
        or event.get("booking_id")
        or payment_entity.get("receipt")
    )

    if not payment_id or not booking_id_str:
        logger.warning("Missing payment_id or booking_id in webhook payload.")
        raise HTTPException(status_code=400, detail="Missing payment_id or booking_id")

    try:
        booking_uuid = uuid.UUID(str(booking_id_str))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format for booking_id")

    # 3. 24-Hour Redis SETNX Idempotency Lock
    idempotency_key = f"apex:idemp:{payment_id}"
    is_new_event = await redis.set(idempotency_key, "locked", nx=True, ex=86400)
    if not is_new_event:
        logger.info(f"🔁 Duplicate webhook event ignored for Payment {payment_id}")
        return JSONResponse(status_code=200, content={"status": "ok", "message": "Duplicate webhook event ignored."})

    # 4. Atomic Postgres Transaction
    stmt = select(Booking).where(Booking.id == booking_uuid).with_for_update()
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()

    if not booking:
        logger.error(f"Booking {booking_uuid} not found in database.")
        raise HTTPException(status_code=444 if False else 404, detail=f"Booking {booking_uuid} not found")

    if booking.status == BookingStatus.PAID_CONFIRMED:
        logger.info(f"Booking {booking_uuid} is already marked as PAID_CONFIRMED.")
        return JSONResponse(status_code=200, content={"status": "ok", "message": "Booking already paid and confirmed."})

    # Generate secure 6-digit Check-In Code
    check_in_code = "".join([secrets.choice("0123456789") for _ in range(6)])

    from_state = booking.status.value if hasattr(booking.status, "value") else str(booking.status)
    booking.status = BookingStatus.PAID_CONFIRMED
    booking.gateway_transaction_id = payment_id
    booking.check_in_code = check_in_code

    # Also update associated Slot status to BOOKED
    slot_stmt = select(Slot).where(Slot.id == booking.slot_id)
    slot_res = await db.execute(slot_stmt)
    slot = slot_res.scalar_one_or_none()
    if slot:
        slot.status = SlotStatus.BOOKED

    # Audit Logging
    audit = AuditLog(
        entity_name="Booking",
        entity_id=booking.id,
        trigger_event_id=payment_id,
        from_state=from_state,
        to_state=BookingStatus.PAID_CONFIRMED.value,
        payload={"payment_id": payment_id, "check_in_code": check_in_code}
    )
    db.add(audit)
    await db.commit()

    logger.info(f"🎉 Booking {booking.id} PAID_CONFIRMED! Check-in code: {check_in_code}")

    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "message": "Payment confirmed and check-in code issued.",
            "booking_id": str(booking.id),
            "check_in_code": check_in_code
        }
    )
