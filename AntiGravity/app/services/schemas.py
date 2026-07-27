# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI TrueLark MIDGO Dual-Output Schemas & 30-Intent FSG Taxonomy

from pydantic import BaseModel, Field

# ==========================================
# 1. 30-INTENT TAXONOMY & MACRO-STATE MAPPING
# ==========================================
TAXONOMY_30_INTENTS = {
    # Macro-State 1: STATE_LOGISTICS
    "INTENT_CONSULT_FEE": ("M1_STATE_LOGISTICS", "Standard consultation pricing"),
    "INTENT_HOURS_WEEKEND": ("M1_STATE_LOGISTICS", "Saturday/Sunday shift verification"),
    "INTENT_CLINIC_TIMINGS": ("M1_STATE_LOGISTICS", "Daily opening/closing hours"),
    "INTENT_EMERGENCY_BOOKING": ("M1_STATE_LOGISTICS", "Priority pain scheduling"),
    "INTENT_LANGUAGE_SUPPORT": ("M1_STATE_LOGISTICS", "Kannada, Hindi, English preference"),
    "INTENT_PARKING_VALET": ("M1_STATE_LOGISTICS", "Facility parking metadata"),
    "INTENT_TELE_DENTISTRY": ("M1_STATE_LOGISTICS", "Virtual consultation flow"),
    "INTENT_STERILIZATION_PROTOCOLS": ("M1_STATE_LOGISTICS", "Safety compliance & sterilization"),

    # Macro-State 2: STATE_FINANCE
    "INTENT_INSURANCE_CLAIM": ("M2_STATE_FINANCE", "TPA partnership & insurance verification"),
    "INTENT_EMI_PLANS": ("M2_STATE_FINANCE", "Zero-cost 0% EMI financing options"),
    "INTENT_COST_RCT": ("M2_STATE_FINANCE", "Root canal price ranges"),
    "INTENT_COST_IMPLANTS": ("M2_STATE_FINANCE", "Implant tiers & pricing brackets"),
    "INTENT_WARRANTY_CARD": ("M2_STATE_FINANCE", "Clinic warranty terms for crowns/implants"),

    # Macro-State 3: STATE_PREVENTIVE
    "INTENT_SCALING_DURATION": ("M3_STATE_PREVENTIVE", "Teeth cleaning time estimates"),
    "INTENT_BLEEDING_GUMS": ("M3_STATE_PREVENTIVE", "Periodontal check-up triage"),
    "INTENT_TOOTH_SENSITIVITY": ("M3_STATE_PREVENTIVE", "Diagnostic evaluation for sensitivity"),
    "INTENT_DIAGNOSTIC_XRAY": ("M3_STATE_PREVENTIVE", "On-site OPG & digital X-ray check"),
    "INTENT_RCT_SITTINGS": ("M3_STATE_PREVENTIVE", "Visit count expectations for root canals"),

    # Macro-State 4: STATE_COSMETIC_SURGICAL
    "INTENT_TEETH_WHITENING": ("M4_STATE_COSMETIC_SURGICAL", "In-office vs. home whitening kits"),
    "INTENT_ALIGNERS_BRACES": ("M4_STATE_COSMETIC_SURGICAL", "Clear aligners vs. metal/ceramic braces"),
    "INTENT_ORTHODONTIC_COST": ("M4_STATE_COSMETIC_SURGICAL", "Orthodontic treatment pricing"),
    "INTENT_WISDOM_EXTRACTION": ("M4_STATE_COSMETIC_SURGICAL", "Surgical wisdom tooth extraction"),
    "INTENT_CROWNS_BRIDGES": ("M4_STATE_COSMETIC_SURGICAL", "Zirconia & porcelain crown lifespans"),
    "INTENT_VENEERS_LIFESPAN": ("M4_STATE_COSMETIC_SURGICAL", "Porcelain & composite veneers"),
    "INTENT_BRIDGE_VS_IMPLANT": ("M4_STATE_COSMETIC_SURGICAL", "Comparative clinical matrix"),
    "INTENT_DENTURES_ELDERLY": ("M4_STATE_COSMETIC_SURGICAL", "Complete & partial dentures"),
    "INTENT_LASER_DENTISTRY": ("M4_STATE_COSMETIC_SURGICAL", "Soft & hard tissue laser treatment"),
    "INTENT_PEDIATRIC_DENTISTRY": ("M4_STATE_COSMETIC_SURGICAL", "Specialized children's dental care"),

    # Macro-State 5: STATE_EMERGENCY
    "INTENT_TRAUMA_FIRST_AID": ("M5_STATE_EMERGENCY", "Critical first-aid & knocked-out tooth triage"),
    "INTENT_POST_OP_CARE": ("M5_STATE_EMERGENCY", "Post-operative extraction recovery guide"),
}

# ==========================================
# 2. PYDANTIC V2 DUAL-OUTPUT SCHEMA
# ==========================================
class MIDGODentalResponse(BaseModel):
    """TrueLark MIDGO Dual-Output Pydantic v2 Schema for State Extraction and Conversational Pivot Generation."""

    extracted_name: str = Field(
        default="",
        description="Patient's full name if mentioned in this turn or previous context, otherwise empty string."
    )
    extracted_symptom_or_reason: str = Field(
        default="",
        description="Core symptom, reason for visit, or emergency status if mentioned, otherwise empty string."
    )
    classified_intent: str = Field(
        default="INTENT_CONSULT_FEE",
        description=(
            "Must be classified into EXACTLY ONE of the 30 recognized intent keys: "
            "INTENT_CONSULT_FEE, INTENT_HOURS_WEEKEND, INTENT_CLINIC_TIMINGS, INTENT_EMERGENCY_BOOKING, "
            "INTENT_LANGUAGE_SUPPORT, INTENT_PARKING_VALET, INTENT_TELE_DENTISTRY, INTENT_STERILIZATION_PROTOCOLS, "
            "INTENT_INSURANCE_CLAIM, INTENT_EMI_PLANS, INTENT_COST_RCT, INTENT_COST_IMPLANTS, INTENT_WARRANTY_CARD, "
            "INTENT_SCALING_DURATION, INTENT_BLEEDING_GUMS, INTENT_TOOTH_SENSITIVITY, INTENT_DIAGNOSTIC_XRAY, INTENT_RCT_SITTINGS, "
            "INTENT_TEETH_WHITENING, INTENT_ALIGNERS_BRACES, INTENT_ORTHODONTIC_COST, INTENT_WISDOM_EXTRACTION, INTENT_CROWNS_BRIDGES, "
            "INTENT_VENEERS_LIFESPAN, INTENT_BRIDGE_VS_IMPLANT, INTENT_DENTURES_ELDERLY, INTENT_LASER_DENTISTRY, INTENT_PEDIATRIC_DENTISTRY, "
            "INTENT_TRAUMA_FIRST_AID, INTENT_POST_OP_CARE."
        )
    )
    patient_reply: str = Field(
        ...,
        description=(
            "Dynamic, empathetic message back to the patient. "
            "MIDGO Rule: Address tangents, FAQs, or clinical queries warmly in sentence 1, "
            "then smoothly pivot back to securing the patient's name or consultation slot unless it is an emergency."
        )
    )
