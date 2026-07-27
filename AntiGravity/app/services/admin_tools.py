# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Doctor Command Center - Admin Tool Registry & Financial Ledger Services

import logging
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, Any, Callable, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking, BookingStatus
from app.models.slot import Slot
from app.models.patient import Patient

logger = logging.getLogger("APEX_AI_ADMIN_TOOLS")


# ---------------------------------------------------------
# Doctor/Admin Tool Input Schemas
# ---------------------------------------------------------

class DailyLedgerInput(BaseModel):
    target_date: str = Field(description="Target date for clinic ledger in YYYY-MM-DD format.")


class RevenueReportInput(BaseModel):
    start_date: str = Field(description="Start date for revenue report in YYYY-MM-DD format.")
    end_date: str = Field(description="End date for revenue report in YYYY-MM-DD format.")


# ---------------------------------------------------------
# Doctor Admin Tools Registry
# ---------------------------------------------------------

class AdminToolsRegistry:
    """Exclusive Action Registry for Doctor Executive Assistant AI Agent."""

    _registry: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, input_schema: type[BaseModel]):
        """Decorator registering admin tools."""
        def decorator(func: Callable):
            cls._registry[name] = {"func": func, "schema": input_schema}
            logger.info(f"👨‍⚕️ Registered Doctor Admin Tool: '{name}'")
            return func
        return decorator

    @classmethod
    async def execute(cls, name: str, db: AsyncSession, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Validates and executes doctor admin tool."""
        if name not in cls._registry:
            return {"success": False, "error": f"Tool '{name}' is not authorized or registered in AdminToolsRegistry."}

        tool_meta = cls._registry[name]
        try:
            validated = tool_meta["schema"](**kwargs)
            return await tool_meta["func"](db=db, **validated.model_dump())
        except Exception as e:
            return {"success": False, "error": f"Validation/Execution error in Admin tool '{name}': {e}"}


# ---------------------------------------------------------
# Doctor Executive Tools Implementation
# ---------------------------------------------------------

@AdminToolsRegistry.register(name="get_daily_ledger", input_schema=DailyLedgerInput)
async def get_daily_ledger(db: AsyncSession, target_date: str) -> Dict[str, Any]:
    """Queries Postgres for all appointment bookings on target date for doctor's daily schedule."""
    try:
        query_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    except ValueError:
        return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD format."}

    stmt = (
        select(Booking, Slot, Patient)
        .join(Slot, Booking.slot_id == Slot.id)
        .join(Patient, Booking.patient_id == Patient.id)
        .where(Slot.date == query_date)
        .order_by(Slot.time)
    )
    result = await db.execute(stmt)
    records = result.all()

    ledger_items = []
    for booking, slot, patient in records:
        ledger_items.append({
            "time": slot.time.strftime("%I:%M %p"),
            "patient_name": patient.name or "Anonymous Patient",
            "phone_number": patient.phone_number,
            "status": booking.status.value if hasattr(booking.status, "value") else str(booking.status),
            "procedure": booking.procedure_name,
            "symptoms_reported": booking.symptoms_reported or "None specified",
            "check_in_code": booking.check_in_code,
            "expected_revenue": f"₹{booking.expected_revenue:,.2f}"
        })

    return {
        "success": True,
        "date": target_date,
        "total_appointments": len(ledger_items),
        "appointments": ledger_items
    }


@AdminToolsRegistry.register(name="get_revenue_report", input_schema=RevenueReportInput)
async def get_revenue_report(db: AsyncSession, start_date: str, end_date: str) -> Dict[str, Any]:
    """Queries Postgres for total expected revenue across CONFIRMED or CHECKED_IN bookings."""
    try:
        start_d = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_d = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD format."}

    stmt = (
        select(
            func.count(Booking.id).label("total_count"),
            func.coalesce(func.sum(Booking.expected_revenue), Decimal("0.00")).label("total_revenue")
        )
        .join(Slot, Booking.slot_id == Slot.id)
        .where(
            and_(
                Slot.date >= start_d,
                Slot.date <= end_d,
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN])
            )
        )
    )
    result = await db.execute(stmt)
    row = result.one()
    total_count = row.total_count or 0
    total_revenue = Decimal(str(row.total_revenue))

    return {
        "success": True,
        "start_date": start_date,
        "end_date": end_date,
        "confirmed_appointments": total_count,
        "total_expected_revenue": f"₹{total_revenue:,.2f}",
        "raw_revenue_amount": str(total_revenue)
    }
