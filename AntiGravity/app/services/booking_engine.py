"""Code-Based Confirmation Engine, slot reservations, and check-in verifications."""

import uuid
import random
import string
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking, BookingStatus
from app.models.slot import Slot, SlotStatus
from app.models.patient import Patient
from app.models.audit_log import AuditLog
from app.core.database import AsyncSessionLocal

logger = logging.getLogger("APEX_AI_BOOKING_ENGINE")


def generate_check_in_code() -> str:
    """Generates unique 6-character check-in code formatted as APX-XXXX."""
    digits = "".join(random.choices(string.digits, k=4))
    return f"APX-{digits}"


async def log_audit_event_async(
    entity_name: str,
    entity_id: uuid.UUID,
    trigger_event_id: str,
    from_state: str,
    to_state: str,
    payload: Optional[Dict[str, Any]] = None
):
    """Asynchronously logs state mutations into Postgres AuditLog."""
    try:
        async with AsyncSessionLocal() as session:
            audit = AuditLog(
                entity_name=entity_name,
                entity_id=entity_id,
                trigger_event_id=trigger_event_id,
                from_state=from_state,
                to_state=to_state,
                payload=payload or {}
            )
            session.add(audit)
            await session.commit()
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")


async def create_booking(
    db: AsyncSession,
    patient_id: uuid.UUID,
    slot_id: uuid.UUID,
    patient_symptoms: str,
    procedure_name: str = "General Consultation"
) -> Dict[str, Any]:
    """Reserves slot, updates status to SLOT_HELD, and returns unique check-in code."""
    stmt = select(Slot).where(Slot.id == slot_id).with_for_update()
    result = await db.execute(stmt)
    slot = result.scalar_one_or_none()

    if not slot or slot.status != SlotStatus.AVAILABLE:
        return {"success": False, "error": "Requested appointment slot is no longer available."}

    slot.status = SlotStatus.HELD
    code = generate_check_in_code()

    booking = Booking(
        slot_id=slot.id,
        patient_id=patient_id,
        status=BookingStatus.SLOT_HELD,
        check_in_code=code,
        is_code_verified=False,
        procedure_name=procedure_name,
        symptoms_reported=patient_symptoms,
        expected_revenue=slot.consultation_fee or 500.00
    )
    try:
        db.add(booking)
        await db.commit()
    except Exception as e:
        await db.rollback()
        return {"success": False, "error": "Requested appointment slot is no longer available."}

    await log_audit_event_async(
        entity_name="Booking",
        entity_id=booking.id,
        trigger_event_id="SLOT_HELD_RESERVATION",
        from_state="NONE",
        to_state="SLOT_HELD",
        payload={"check_in_code": code, "slot_id": str(slot.id)}
    )

    return {
        "success": True,
        "booking_id": str(booking.id),
        "check_in_code": code,
        "status": "SLOT_HELD",
        "message": f"Slot reserved! Please reply with code {code} to confirm your appointment."
    }


async def confirm_booking_with_code(
    db: AsyncSession,
    code: str,
    phone_number: str
) -> Dict[str, Any]:
    """Validates check-in code and updates booking status to CONFIRMED."""
    clean_code = code.strip().upper()
    stmt = (
        select(Booking, Slot)
        .join(Slot, Booking.slot_id == Slot.id)
        .where(and_(Booking.check_in_code == clean_code, Booking.status == BookingStatus.SLOT_HELD))
    )
    result = await db.execute(stmt)
    row = result.first()

    if not row:
        return {"success": False, "error": f"Invalid or expired check-in code '{clean_code}'."}

    booking, slot = row
    booking.status = BookingStatus.CONFIRMED
    booking.is_code_verified = True
    slot.status = SlotStatus.BOOKED

    await db.commit()

    await log_audit_event_async(
        entity_name="Booking",
        entity_id=booking.id,
        trigger_event_id="CHECK_IN_CODE_CONFIRMED",
        from_state="SLOT_HELD",
        to_state="CONFIRMED",
        payload={"code": clean_code}
    )

    return {
        "success": True,
        "booking_id": str(booking.id),
        "check_in_code": clean_code,
        "status": "CONFIRMED",
        "message": f"Appointment confirmed! Check-in code {clean_code} verified."
    }


async def cancel_booking(db: AsyncSession, code: str) -> Dict[str, Any]:
    """Cancels booking and releases held slot."""
    clean_code = code.strip().upper()
    stmt = (
        select(Booking, Slot)
        .join(Slot, Booking.slot_id == Slot.id)
        .where(Booking.check_in_code == clean_code)
    )
    result = await db.execute(stmt)
    row = result.first()

    if not row:
        return {"success": False, "error": f"No booking found with code '{clean_code}'."}

    booking, slot = row
    from_state = booking.status.value
    booking.status = BookingStatus.CANCELLED
    slot.status = SlotStatus.AVAILABLE

    await db.commit()

    await log_audit_event_async(
        entity_name="Booking",
        entity_id=booking.id,
        trigger_event_id="USER_CANCELLED_BOOKING",
        from_state=from_state,
        to_state="CANCELLED",
        payload={"code": clean_code}
    )

    return {
        "success": True,
        "check_in_code": clean_code,
        "status": "CANCELLED",
        "message": f"Booking {clean_code} cancelled and slot released."
    }
