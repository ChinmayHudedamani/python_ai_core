# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Code-Based Booking Engine & Expiry Manager

import uuid
import secrets
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.slot import Slot, SlotStatus
from app.models.booking import Booking, BookingStatus
from app.models.patient import Patient
from app.models.audit_log import AuditLog

logger = logging.getLogger("APEX_AI_BOOKING_ENGINE")


def generate_check_in_code() -> str:
    """Generates a 6-character unique alphanumeric check-in code (e.g. APX-4928)."""
    random_num = secrets.randbelow(9000) + 1000
    return f"APX-{random_num}"


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
    except Exception as e:
        logger.error(f"❌ Failed to write audit log: {e}")


async def create_booking(
    db: AsyncSession,
    patient_id: uuid.UUID,
    slot_id: uuid.UUID,
    procedure_name: str = "General Consultation"
) -> Dict[str, Any]:
    """Reserves a slot as SLOT_HELD and generates a unique check-in confirmation code."""
    # Verify slot availability
    slot_stmt = select(Slot).where(Slot.id == slot_id).with_for_update()
    slot_res = await db.execute(slot_stmt)
    slot = slot_res.scalar_one_or_none()

    if not slot or slot.status != SlotStatus.AVAILABLE:
        return {"success": False, "error": "Requested appointment slot is no longer available."}

    # Generate unique check-in code
    check_in_code = generate_check_in_code()

    # Update slot status
    slot.status = SlotStatus.HELD

    # Create Booking row
    booking = Booking(
        patient_id=patient_id,
        slot_id=slot_id,
        procedure_name=procedure_name,
        status=BookingStatus.SLOT_HELD,
        check_in_code=check_in_code,
        is_code_verified=False
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)

    await log_audit_event_async(
        entity_name="Booking",
        entity_id=booking.id,
        trigger_event_id="SLOT_RESERVED_CODE_GENERATED",
        from_state=None,
        to_state="SLOT_HELD",
        payload={"check_in_code": check_in_code, "slot_id": str(slot_id)}
    )

    return {
        "success": True,
        "booking_id": str(booking.id),
        "check_in_code": check_in_code,
        "date": str(slot.date),
        "time": slot.time.strftime("%I:%M %p"),
        "doctor": slot.doctor_name
    }


async def confirm_booking_with_code(
    db: AsyncSession,
    code: str,
    phone_number: str
) -> Dict[str, Any]:
    """Confirms booking when patient repeats their unique check-in code."""
    clean_code = code.strip().upper()
    if not clean_code:
        return {"success": False, "error": "Confirmation code cannot be empty."}

    # Query booking matching code
    stmt = (
        select(Booking)
        .join(Patient, Booking.patient_id == Patient.id)
        .where(
            and_(
                Booking.check_in_code == clean_code,
                Patient.phone_number == phone_number
            )
        )
    )
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()

    if not booking:
        return {
            "success": False,
            "error": f"No active booking found matching code '{clean_code}' for phone {phone_number}."
        }

    if booking.status == BookingStatus.CONFIRMED:
        return {
            "success": True,
            "message": f"Booking with code '{clean_code}' is already confirmed!",
            "check_in_code": clean_code
        }

    from_state = booking.status.value
    booking.status = BookingStatus.CONFIRMED
    booking.is_code_verified = True

    # Update associated Slot to BOOKED
    slot_stmt = select(Slot).where(Slot.id == booking.slot_id)
    slot_res = await db.execute(slot_stmt)
    slot = slot_res.scalar_one_or_none()
    if slot:
        slot.status = SlotStatus.BOOKED

    await db.commit()

    await log_audit_event_async(
        entity_name="Booking",
        entity_id=booking.id,
        trigger_event_id="CODE_VERIFIED_BOOKING_CONFIRMED",
        from_state=from_state,
        to_state="CONFIRMED",
        payload={"check_in_code": clean_code, "phone": phone_number}
    )

    return {
        "success": True,
        "message": f"Appointment successfully confirmed with code '{clean_code}'!",
        "booking_id": str(booking.id),
        "check_in_code": clean_code
    }


async def cancel_booking(
    db: AsyncSession,
    code: str,
    phone_number: Optional[str] = None
) -> Dict[str, Any]:
    """Cancels booking matching confirmation code and frees slot back to AVAILABLE."""
    clean_code = code.strip().upper()
    if not clean_code:
        return {"success": False, "error": "Confirmation code cannot be empty."}

    stmt = select(Booking).where(Booking.check_in_code == clean_code)
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()

    if not booking:
        return {"success": False, "error": f"No booking found matching code '{clean_code}'."}

    from_state = booking.status.value
    booking.status = BookingStatus.CANCELLED

    # Reset slot to AVAILABLE
    slot_stmt = select(Slot).where(Slot.id == booking.slot_id)
    slot_res = await db.execute(slot_stmt)
    slot = slot_res.scalar_one_or_none()
    if slot:
        slot.status = SlotStatus.AVAILABLE

    await db.commit()

    await log_audit_event_async(
        entity_name="Booking",
        entity_id=booking.id,
        trigger_event_id="BOOKING_CANCELLED_BY_PATIENT",
        from_state=from_state,
        to_state="CANCELLED",
        payload={"check_in_code": clean_code}
    )

    return {
        "success": True,
        "message": f"Booking with code '{clean_code}' has been cancelled and the slot released.",
        "check_in_code": clean_code
    }
