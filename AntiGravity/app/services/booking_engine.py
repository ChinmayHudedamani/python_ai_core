# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Hybrid Slot Expiry Manager & Async Audit Logger

import uuid
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import select, and_
from app.database import AsyncSessionLocal
from app.models.slot import Slot, SlotStatus
from app.models.booking import Booking, BookingStatus
from app.models.audit_log import AuditLog

logger = logging.getLogger("APEX_AI_BOOKING_ENGINE")


async def log_audit_event_async(
    entity_name: str,
    entity_id: uuid.UUID,
    trigger_event_id: str,
    from_state: Optional[str],
    to_state: str,
    payload: Optional[Dict[str, Any]] = None
) -> None:
    """Non-blocking fire-and-forget task inserting an AuditLog row into Postgres."""
    try:
        async with AsyncSessionLocal() as session:
            audit = AuditLog(
                entity_name=entity_name,
                entity_id=entity_id,
                trigger_event_id=trigger_event_id,
                from_state=from_state,
                to_state=to_state,
                payload=payload,
                timestamp=datetime.now(timezone.utc)
            )
            session.add(audit)
            await session.commit()
            logger.info(f"✅ Audit Log written: {entity_name} {entity_id} -> {to_state}")
    except Exception as e:
        logger.error(f"❌ Failed to write audit log asynchronously: {e}")


async def release_slot_after_timeout(
    slot_id: uuid.UUID,
    hold_duration_seconds: int = 300,
    phone_number: Optional[str] = None
) -> None:
    """Async background task that sleeps 300s (5 min) and releases unconfirmed slots."""
    logger.info(f"⏳ Spawned 5-minute slot release timer for Slot {slot_id} ({hold_duration_seconds}s)")
    await asyncio.sleep(hold_duration_seconds)

    try:
        async with AsyncSessionLocal() as session:
            stmt = select(Slot).where(Slot.id == slot_id)
            result = await session.execute(stmt)
            slot = result.scalar_one_or_none()

            if not slot:
                logger.warning(f"Slot {slot_id} not found during timeout evaluation.")
                return

            if slot.status == SlotStatus.HELD:
                # Check associated booking
                booking_stmt = select(Booking).where(Booking.slot_id == slot_id)
                booking_res = await session.execute(booking_stmt)
                booking = booking_res.scalar_one_or_none()

                # If booking exists and is unpaid, release slot
                if not booking or booking.status in [BookingStatus.SLOT_HELD, BookingStatus.PAYMENT_PENDING]:
                    slot.status = SlotStatus.AVAILABLE
                    slot.held_until = None
                    await session.commit()

                    logger.info(f"🔓 Slot {slot_id} automatically released back to AVAILABLE inventory.")

                    # Log Audit Event
                    await log_audit_event_async(
                        entity_name="Slot",
                        entity_id=slot_id,
                        trigger_event_id="SLOT_EXPIRY_TIMEOUT_RELEASE",
                        from_state="HELD",
                        to_state="AVAILABLE",
                        payload={"phone_number": phone_number, "reason": "5_minute_unpaid_timeout"}
                    )

                    # Trigger WhatsApp Nudge Notification
                    if phone_number:
                        nudge_msg = (
                            "Your 5-minute hold on this appointment slot has expired. "
                            "Would you like me to find another convenient time for your consultation?"
                        )
                        logger.info(f"📲 WhatsApp Nudge sent to {phone_number}: '{nudge_msg}'")

    except Exception as e:
        logger.error(f"❌ Exception in slot release timer for {slot_id}: {e}")


def schedule_slot_release(
    slot_id: uuid.UUID,
    hold_duration_seconds: int = 300,
    phone_number: Optional[str] = None
) -> asyncio.Task:
    """Fires a background task to release the slot after timeout."""
    return asyncio.create_task(
        release_slot_after_timeout(
            slot_id=slot_id,
            hold_duration_seconds=hold_duration_seconds,
            phone_number=phone_number
        )
    )
