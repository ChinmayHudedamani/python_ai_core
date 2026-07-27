"""SQLite Knowledge Base Seed Script."""

import sys
import logging
from pathlib import Path
from decimal import Decimal
from sqlmodel import Session, SQLModel, select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.sqlite_db import sqlite_engine
from app.models.kb import (
    ClinicProfile,
    DoctorProfile,
    ProcedureCatalog,
    ClinicFAQ,
    ClinicalTriageRule
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SEED_KB")


def seed_knowledge_base():
    """Populates SQLite database with clinic metadata, procedure catalog, and triage rules."""
    logger.info("Seeding SQLite Relational Knowledge Base (clinic_kb.db)...")
    SQLModel.metadata.create_all(sqlite_engine)

    with Session(sqlite_engine) as session:
        # Check if already seeded
        existing = session.exec(select(ClinicProfile)).first()
        if existing:
            logger.info("Knowledge Base already contains data. Skipping re-seed.")
            return

        clinic = ClinicProfile(
            clinic_name="Apex Dental Center & Implant Institute",
            address="104, 80 Feet Road, 4th Block, Koramangala, Bengaluru, Karnataka 560034",
            primary_phone="+91-9988776655",
            emergency_phone="+91-9988776655",
            operating_hours="Monday - Saturday: 09:00 AM - 08:30 PM | Sunday: 10:00 AM - 02:00 PM",
            accepted_insurance=["HDFC ERGO", "Star Health", "Max Bupa", "ICICI Lombard", "Navi General"]
        )
        session.add(clinic)

        doc1 = DoctorProfile(
            doctor_name="Dr. Chinmay Hudedamani",
            specialization="Implantologist & Oral Surgeon",
            qualification="BDS, MDS (Oral & Maxillofacial Surgery)",
            experience_years=14,
            available_days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            consultation_fee=Decimal("700.00")
        )
        doc2 = DoctorProfile(
            doctor_name="Dr. Rajesh Nair",
            specialization="Endodontist (Root Canal Specialist)",
            qualification="BDS, MDS (Conservative Dentistry & Endodontics)",
            experience_years=11,
            available_days=["Monday", "Wednesday", "Friday", "Saturday"],
            consultation_fee=Decimal("600.00")
        )
        session.add(doc1)
        session.add(doc2)

        procedures = [
            ProcedureCatalog(
                procedure_name="Microscopic Single-Sitting Root Canal (RCT)",
                category="Endodontics",
                estimated_duration_minutes=45,
                price_min=Decimal("4500.00"),
                price_max=Decimal("7500.00"),
                pre_op_instructions="Eat a light meal before appointment. Continue routine blood pressure medications.",
                post_op_instructions="Avoid chewing on the treated side until numbness wears off. Take prescribed analgesics."
            ),
            ProcedureCatalog(
                procedure_name="Dental Implant Placement (Nobel Biocare / Straumann)",
                category="Implantology",
                estimated_duration_minutes=60,
                price_min=Decimal("25000.00"),
                price_max=Decimal("45000.00"),
                pre_op_instructions="Complete CBCT 3D Scan prior to surgery. Antibiotic prophylaxis as advised.",
                post_op_instructions="Apply ice pack externally for 20 mins on/off. Soft cold diet for 48 hours."
            ),
            ProcedureCatalog(
                procedure_name="Invisalign® Clear Aligners Consultation",
                category="Orthodontics",
                estimated_duration_minutes=30,
                price_min=Decimal("60000.00"),
                price_max=Decimal("150000.00"),
                pre_op_instructions="No special preparation required.",
                post_op_instructions="Wear aligners 22 hours daily. Clean with soft toothbrush and cold water."
            )
        ]
        for p in procedures:
            session.add(p)

        triage_rules = [
            ClinicalTriageRule(
                keyword="knocked out tooth",
                category="TRAUMA",
                urgency_level="CRITICAL_EMERGENCY",
                first_aid_instructions="Store tooth in cold milk or saline immediately! Do NOT touch the root! Reach clinic within 60 mins!"
            ),
            ClinicalTriageRule(
                keyword="khoon nikal raha hai",
                category="BLEEDING",
                urgency_level="CRITICAL_EMERGENCY",
                first_aid_instructions="Apply firm pressure with clean gauze or tea bag for 30 minutes. Keep head elevated!"
            ),
            ClinicalTriageRule(
                keyword="दांत निकल गया",
                category="TRAUMA",
                urgency_level="CRITICAL_EMERGENCY",
                first_aid_instructions="दांत को दूध में रखें। तुरंत 60 मिनट के अंदर क्लिनिक आएं!"
            )
        ]
        for tr in triage_rules:
            session.add(tr)

        session.commit()
        logger.info("SQLite Knowledge Base successfully seeded!")


if __name__ == "__main__":
    seed_knowledge_base()
