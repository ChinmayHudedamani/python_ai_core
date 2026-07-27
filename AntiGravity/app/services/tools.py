# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI ActionRegistry & LLM Deterministic Tools

import logging
from typing import Dict, Any, Callable, Optional, List
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.booking_engine import (
    confirm_booking_with_code as engine_confirm,
    cancel_booking as engine_cancel
)

logger = logging.getLogger("APEX_AI_TOOLS")


# ---------------------------------------------------------
# Pydantic Tool Input Schemas
# ---------------------------------------------------------

class ConfirmBookingInput(BaseModel):
    code: str = Field(description="The unique 6-character check-in confirmation code (e.g. APX-4928).")
    phone_number: str = Field(description="Patient's validated Indian mobile number (+91).")


class CancelBookingInput(BaseModel):
    code: str = Field(description="The unique 6-character check-in confirmation code to cancel.")


class SlotLookupInput(BaseModel):
    target_date: str = Field(description="Target date expression in YYYY-MM-DD format.")
    doctor_name: Optional[str] = Field(default="Dr. Chinmay Hudedamani", description="Name of the attending doctor.")


# ---------------------------------------------------------
# ActionRegistry Implementation
# ---------------------------------------------------------

class ActionRegistry:
    """Central Action Registry for LLM Tool Execution."""

    _registry: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, input_schema: type[BaseModel]):
        """Decorator to register deterministic tools with Pydantic schemas."""
        def decorator(func: Callable):
            cls._registry[name] = {
                "func": func,
                "schema": input_schema
            }
            logger.info(f"⚙️ Registered Action Tool: '{name}'")
            return func
        return decorator

    @classmethod
    async def execute(cls, name: str, db: AsyncSession, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Validates input against Pydantic schema and executes registered tool function."""
        if name not in cls._registry:
            return {"success": False, "error": f"Tool '{name}' is not registered in ActionRegistry."}

        tool_meta = cls._registry[name]
        schema_cls = tool_meta["schema"]
        func = tool_meta["func"]

        try:
            validated_input = schema_cls(**kwargs)
            return await func(db=db, **validated_input.model_dump())
        except Exception as e:
            logger.error(f"❌ Error executing tool '{name}': {e}")
            return {"success": False, "error": f"Validation/Execution error for tool '{name}': {e}"}


# ---------------------------------------------------------
# Tool Registrations
# ---------------------------------------------------------

@ActionRegistry.register(name="confirm_booking_with_code", input_schema=ConfirmBookingInput)
async def tool_confirm_booking(db: AsyncSession, code: str, phone_number: str) -> Dict[str, Any]:
    """Confirms held slot booking using check-in code."""
    return await engine_confirm(db=db, code=code, phone_number=phone_number)


@ActionRegistry.register(name="cancel_booking", input_schema=CancelBookingInput)
async def tool_cancel_booking(db: AsyncSession, code: str) -> Dict[str, Any]:
    """Cancels held/confirmed booking using check-in code."""
    return await engine_cancel(db=db, code=code)
