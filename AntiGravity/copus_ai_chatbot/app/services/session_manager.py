# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# Copus AI / APEX AI — Enterprise Session State Machine Module

try:
    from session_manager import (
        APEXBaseException,
        InvalidSessionStateException,
        SecurityViolationException,
        TierAccessDeniedException,
        StructuredJsonLogger,
        InputSanitizationPipeline,
        PatientSessionState,
        SessionStateMachine
    )
except ImportError:
    from copus_ai_chatbot.session_manager import (
        APEXBaseException,
        InvalidSessionStateException,
        SecurityViolationException,
        TierAccessDeniedException,
        StructuredJsonLogger,
        InputSanitizationPipeline,
        PatientSessionState,
        SessionStateMachine
    )
