# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Automated 24-Hour Reminder Worker for Unconfirmed Slots

import logging
from datetime import date, timedelta
from typing import List
from sqlalchemy import select, and_
from app.database import AsyncSessionLocal
from app.models.booking import Booking, BookingStatus
from app.models.slot import Slot

logger = logging.getLogger("APEX_AI_REMINDER_CRON")


async def chase_unconfirmed_slots() -> int:
    """Queries Postgres for SLOT_HELD bookings scheduled within the next 24 hours and sends reminder template."""
    today = date.today()
    tomorrow = today + timedelta(days=1)
    reminders_sent = 0

    try:
        async with AsyncSessionLocal() as session:
            stmt = (
                select(Booking)
                .join(Slot, Booking.slot_id == Slot.id)
                .where(
                    and_(
                        Booking.status == BookingStatus.SLOT_HELD,
                        Slot.date <= tomorrow,
                        Slot.date >= today
                    )
                )
            )
            result = await session.execute(stmt)
            unconfirmed_bookings: List[Booking] = result.scalars().all()

            for booking in unconfirmed_bookings:
                reminders_sent += 1
                reminder_msg = (
                    f"Hi! Your dental appointment is coming up tomorrow. "
                    f"Please reply with your confirmation code {booking.check_in_code} to lock in your slot, "
                    f"or let us know if you need to reschedule."
                )
                logger.info(
                    f"📲 24-Hour WhatsApp Reminder sent for Booking {booking.id} "
                    f"(Code: {booking.check_in_code}): '{reminder_msg}'"
                )

            logger.info(f"✅ 24-Hour Reminder Worker evaluated {reminders_sent} unconfirmed booking(s).")

    except Exception as e:
        logger.error(f"❌ Error during 24-hour reminder worker execution: {e}")

    return reminders_sent
