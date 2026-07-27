# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Cognitive Pydantic Schemas & Auto-Handoff Rules

import enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class UserSentimentEnum(str, enum.Enum):
    CALM = "CALM"
    FRUSTRATED = "FRUSTRATED"
    DISTRESSED = "DISTRESSED"
    URGENT = "URGENT"


class ToolCall(BaseModel):
    name: str = Field(description="Name of the deterministic tool to execute.")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments dictionary to pass to the tool.")


class LLMResponse(BaseModel):
    confidence_score: float = Field(description="LLM self-evaluated confidence score between 0.0 and 1.0.")
    user_sentiment: UserSentimentEnum = Field(description="Detected emotional state of the patient.")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="List of tool calls to execute.")
    response_text: str = Field(description="Conversational response message to patient.")

    @field_validator("confidence_score")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("confidence_score must be between 0.0 and 1.0")
        return v


def evaluate_auto_handoff_rules(llm_response: LLMResponse) -> Dict[str, Any]:
    """Auto-Handoff Rule Evaluator: Intercepts flow if confidence < 0.75 or sentiment is DISTRESSED/FRUSTRATED."""
    should_handoff = (
        llm_response.confidence_score < 0.75
        or llm_response.user_sentiment in [UserSentimentEnum.DISTRESSED, UserSentimentEnum.FRUSTRATED]
    )

    if should_handoff:
        return {
            "trigger_handoff": True,
            "reason": (
                f"Confidence below threshold ({llm_response.confidence_score:.2f}) "
                f"or sentiment elevated ({llm_response.user_sentiment.value})."
            ),
            "override_text": (
                "I want to make sure you get the absolute best care. "
                "I am connecting you directly to our lead receptionist for personal assistance right away!"
            )
        }

    return {
        "trigger_handoff": False,
        "reason": None,
        "override_text": None
    }
