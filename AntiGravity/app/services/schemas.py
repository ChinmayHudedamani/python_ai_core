# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI TrueLark MIDGO Dual-Output Pydantic Schemas

from pydantic import BaseModel, Field


class MIDGODentalResponse(BaseModel):
    """TrueLark MIDGO Dual-Output Schema for State Extraction and Conversational Pivot Generation."""

    extracted_name: str = Field(
        default="",
        description="Patient's full name if mentioned in this turn or previous context, otherwise empty string."
    )
    extracted_symptom_or_reason: str = Field(
        default="",
        description="Core symptom, reason for visit, or emergency status if mentioned, otherwise empty string."
    )
    classified_intent: str = Field(
        default="BOOKING_SLOT",
        description="Intent tag: BOOKING_SLOT, FAQ_INQUIRY, EMERGENCY_TRIAGE, or STATUS_LOOKUP."
    )
    patient_reply: str = Field(
        ...,
        description=(
            "Dynamic, empathetic message back to the patient. "
            "MIDGO Rule: If the patient brought up a tangent or FAQ (e.g., parking, pricing, insurance, tablets, location), "
            "address it warmly and reassuringly in the first sentence, then smoothly pivot back to collecting the next missing goal field."
        )
    )
