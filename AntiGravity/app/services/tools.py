# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI ActionRegistry & LLM Deterministic Tools with Required Symptom Capture

import uuid
import logging
from typing import Dict, Any, Callable, Optional
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.booking_engine import (
    create_booking as engine_create_booking,
    confirm_booking_with_code as engine_confirm,
    cancel_booking as engine_cancel
)

logger = logging.getLogger("APEX_AI_TOOLS")


# ---------------------------------------------------------
# Patient Pydantic Tool Input Schemas
# ---------------------------------------------------------

class CreateBookingInput(BaseModel):
    slot_id: str = Field(description="UUID string of the target appointment slot.")
    patient_id: str = Field(description="UUID string of the patient.")
    patient_symptoms: str = Field(
        ...,
        description="The primary symptom or reason for visit. If the user has not provided this, you MUST ask them for it before calling this tool."
    )
    procedure_name: Optional[str] = Field(default="General Consultation", description="Name of the requested procedure.")


class ConfirmBookingInput(BaseModel):
    code: str = Field(description="The unique 6-character check-in confirmation code (e.g. APX-4928).")
    phone_number: str = Field(description="Patient's validated Indian mobile number (+91).")


class CancelBookingInput(BaseModel):
    code: str = Field(description="The unique 6-character check-in confirmation code to cancel.")


# ---------------------------------------------------------
# Patient Action Registry
# ---------------------------------------------------------

class PatientToolsRegistry:
    """Action Registry exposing tools for Patient Concierge AI Agent."""

    _registry: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, input_schema: type[BaseModel]):
        """Decorator registering patient concierge tools."""
        def decorator(func: Callable):
            cls._registry[name] = {"func": func, "schema": input_schema}
            logger.info(f"⚙️ Registered Patient Tool: '{name}'")
            return func
        return decorator

    @classmethod
    async def execute(cls, name: str, db: AsyncSession, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Validates and executes patient tool."""
        if name not in cls._registry:
            return {"success": False, "error": f"Tool '{name}' not found in PatientToolsRegistry."}

        tool_meta = cls._registry[name]
        try:
            validated = tool_meta["schema"](**kwargs)
            return await tool_meta["func"](db=db, **validated.model_dump())
        except Exception as e:
            return {"success": False, "error": f"Validation/Execution error in '{name}': {e}"}


# ---------------------------------------------------------
# Registered Patient Tools
# ---------------------------------------------------------

@PatientToolsRegistry.register(name="create_booking", input_schema=CreateBookingInput)
async def tool_create_booking(
    db: AsyncSession,
    slot_id: str,
    patient_id: str,
    patient_symptoms: str,
    procedure_name: str = "General Consultation"
) -> Dict[str, Any]:
    """Reserves slot, captures symptoms, and returns check-in code."""
    try:
        s_id = uuid.UUID(slot_id)
        p_id = uuid.UUID(patient_id)
    except ValueError as e:
        return {"success": False, "error": f"Invalid UUID format: {e}"}

    return await engine_create_booking(
        db=db,
        patient_id=p_id,
        slot_id=s_id,
        patient_symptoms=patient_symptoms,
        procedure_name=procedure_name
    )


@PatientToolsRegistry.register(name="confirm_booking_with_code", input_schema=ConfirmBookingInput)
async def tool_confirm_booking(db: AsyncSession, code: str, phone_number: str) -> Dict[str, Any]:
    """Confirms booking using check-in code."""
    return await engine_confirm(db=db, code=code, phone_number=phone_number)


@PatientToolsRegistry.register(name="cancel_booking", input_schema=CancelBookingInput)
async def tool_cancel_booking(db: AsyncSession, code: str) -> Dict[str, Any]:
    """Cancels booking using check-in code."""
    return await engine_cancel(db=db, code=code)
