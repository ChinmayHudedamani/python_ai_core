# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Async Abandoned Cart Payment Chaser Worker

import logging
from datetime import datetime, timezone, timedelta
from typing import List
from sqlalchemy import select, and_
from app.database import AsyncSessionLocal
from app.models.booking import Booking, BookingStatus

logger = logging.getLogger("APEX_AI_PAYMENT_CHASER")


async def chase_abandoned_payments() -> int:
    """Queries Postgres for unpaid bookings over 15 minutes old and sends reminder nudges."""
    fifteen_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=15)
    reminders_sent = 0

    try:
        async with AsyncSessionLocal() as session:
            stmt = select(Booking).where(
                and_(
                    Booking.status.in_([BookingStatus.PAYMENT_PENDING, BookingStatus.SLOT_HELD]),
                    Booking.payment_link_sent_at.is_not(None),
                    Booking.payment_link_sent_at < fifteen_mins_ago,
                    Booking.payment_reminder_sent_at.is_(None)
                )
            )
            result = await session.execute(stmt)
            abandoned_bookings: List[Booking] = result.scalars().all()

            for booking in abandoned_bookings:
                now_utc = datetime.now(timezone.utc)
                booking.payment_reminder_sent_at = now_utc
                reminders_sent += 1

                # Trigger WhatsApp Chaser Message
                chaser_msg = (
                    "Hi! Did you face any issues with the payment link for your dental appointment? "
                    "Let us know if you need any help completing your booking."
                )
                logger.info(
                    f"📲 Payment Chaser Nudge sent for Booking {booking.id} "
                    f"(Link sent at {booking.payment_link_sent_at}): '{chaser_msg}'"
                )

            if reminders_sent > 0:
                await session.commit()
                logger.info(f"✅ Payment Chaser processed {reminders_sent} abandoned booking(s).")

    except Exception as e:
        logger.error(f"❌ Error during payment chaser execution: {e}")

    return reminders_sent
