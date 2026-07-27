# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Post-Consultation Digital Care Card & Retention Recall Engine

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Final, Optional


class ProcedureCategory(str, Enum):
    EXTRACTION = "EXTRACTION_SURGERY"
    ROOT_CANAL = "ROOT_CANAL_TREATMENT"
    ALIGNERS = "CLEAR_ALIGNERS"
    GENERAL_CLEANING = "SCALING_CLEANING"


@dataclass(slots=True, frozen=True)
class DigitalCareCard:
    """Memory-optimized frozen slots dataclass for post-op care guidelines."""
    procedure: ProcedureCategory
    title: str
    do_rules: str
    dont_rules: str
    emergency_symptoms: str
    recall_days: int


class CareCardService:
    """Post-Consultation Digital Care Card & Retention Recall Engine."""

    _CARE_REGISTRY: Final[Dict[ProcedureCategory, DigitalCareCard]] = {
        ProcedureCategory.EXTRACTION: DigitalCareCard(
            procedure=ProcedureCategory.EXTRACTION,
            title="🩸 Surgical Extraction Recovery Instructions",
            do_rules="• Keep firm gauze pressure for 45 minutes.\n• Eat cold, soft foods (ice cream, yogurt).\n• Take prescribed medications on time.",
            dont_rules="• Do NOT spit, smoke, or drink through a straw for 24 hours.\n• Avoid hot or spicy liquid meals.",
            emergency_symptoms="Uncontrolled bleeding after 2 hours or severe facial swelling.",
            recall_days=7  # Suture removal / review
        ),
        ProcedureCategory.ROOT_CANAL: DigitalCareCard(
            procedure=ProcedureCategory.ROOT_CANAL,
            title="🦷 Root Canal Post-Treatment Guidelines",
            do_rules="• Chew on the opposite side until final crown placement.\n• Maintain strict brushing and salt-water rinses after 24h.",
            dont_rules="• Do NOT bite hard or sticky foods on the treated tooth.",
            emergency_symptoms="Severe throbbing pain or temporary filling fracture.",
            recall_days=5  # Permanent crown fitting
        ),
        ProcedureCategory.ALIGNERS: DigitalCareCard(
            procedure=ProcedureCategory.ALIGNERS,
            title="😬 Clear Aligner Wear & Hygiene Guidelines",
            do_rules="• Wear aligner trays for 20–22 hours daily.\n• Rinse aligners with cool water before re-inserting.",
            dont_rules="• Never clean aligners with hot water or harsh soaps.",
            emergency_symptoms="Tray cracking or attachment detachment.",
            recall_days=14  # Next tray swap
        ),
        ProcedureCategory.GENERAL_CLEANING: DigitalCareCard(
            procedure=ProcedureCategory.GENERAL_CLEANING,
            title="✨ Professional Scaling & Hygiene Care Card",
            do_rules="• Rinse with warm salt water for 48 hours.\n• Use a soft-bristled toothbrush and fluoride toothpaste.",
            dont_rules="• Avoid extremely hot, cold, or acidic food for 24 hours.",
            emergency_symptoms="Persistent bleeding or severe gum sensitivity.",
            recall_days=180  # 6-Month routine recall
        )
    }

    @classmethod
    def generate_care_card(
        cls, procedure: ProcedureCategory, patient_name: str = "Patient"
    ) -> str:
        """Renders formatted WhatsApp care instructions."""
        card = cls._CARE_REGISTRY.get(procedure)
        if not card:
            return f"📋 Care instructions for {patient_name}: Maintain standard oral hygiene and contact the desk for queries."

        return (
            f"📋 *{card.title}*\n"
            f"Patient: *{patient_name}*\n\n"
            f"✅ *DO'S*:\n{card.do_rules}\n\n"
            f"🚫 *DON'TS*:\n{card.dont_rules}\n\n"
            f"🚨 *WHEN TO CALL US*: {card.emergency_symptoms}\n"
            f"📞 *Emergency Line*: +91-9876543210\n\n"
            f"🔔 *Automated Review Scheduled*: In {card.recall_days} days."
        )


# Backward compatibility helper
def send_post_care_card(patient_phone: str, procedure_type: str = "EXTRACTION") -> str:
    category_map = {
        "EXTRACTION": ProcedureCategory.EXTRACTION,
        "ROOT_CANAL": ProcedureCategory.ROOT_CANAL,
        "ALIGNERS": ProcedureCategory.ALIGNERS,
        "GENERAL": ProcedureCategory.GENERAL_CLEANING
    }
    cat = category_map.get(procedure_type.upper(), ProcedureCategory.GENERAL_CLEANING)
    return CareCardService.generate_care_card(cat, patient_name=patient_phone)
