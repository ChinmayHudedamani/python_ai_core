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


def seed_database():
    """Populates SQLite database with clinic metadata, procedure catalog, and triage rules."""
    logger.info("Seeding SQLite Relational Knowledge Base (clinic_kb.db)...")
    SQLModel.metadata.create_all(sqlite_engine)

    with Session(sqlite_engine) as session:
        existing = session.exec(select(ClinicProfile)).first()
        if existing:
            logger.info("Knowledge Base already contains data. Skipping re-seed.")
            return

        clinic = ClinicProfile(
            name="Apex Dental Center & Implant Institute",
            address="104, 80 Feet Road, 4th Block, Koramangala, Bengaluru, Karnataka 560034",
            landmark="Near Sony World Signal",
            parking_info="Free basement valet parking available",
            operating_hours="Mon-Sat: 09:00 AM - 08:30 PM | Sun: 10:00 AM - 02:00 PM",
            online_consult_available=True,
            accepted_payments="Cash, UPI, Credit/Debit Cards, Bajaj Finserv EMI"
        )
        session.add(clinic)

        doc1 = DoctorProfile(
            name="Dr. Chinmay Hudedamani",
            title="Lead Oral Surgeon & Implantologist",
            qualifications="BDS, MDS (Oral & Maxillofacial Surgery)",
            experience_years=14,
            bio="Senior Specialist in single-day implants and complex bone grafting.",
            specialties="Dental Implants, Surgical Extractions, Trauma Surgery",
            available_days="Mon,Tue,Wed,Thu,Fri,Sat",
            consultation_fee=Decimal("700.00")
        )
        doc2 = DoctorProfile(
            name="Dr. Rajesh Nair",
            title="Senior Endodontist",
            qualifications="BDS, MDS (Conservative Dentistry & Endodontics)",
            experience_years=11,
            bio="Specialist in painless microscope-guided single sitting root canals.",
            specialties="Root Canal, Re-RCT, Cosmetic Restorations",
            available_days="Mon,Wed,Fri,Sat",
            consultation_fee=Decimal("600.00")
        )
        session.add(doc1)
        session.add(doc2)

        procedures = [
            ProcedureCatalog(
                name="Microscopic Single-Sitting Root Canal (RCT)",
                category="Endodontics",
                duration_minutes=45,
                price_min=Decimal("4500.00"),
                price_max=Decimal("7500.00"),
                is_surgical=False,
                prerequisites="Pre-op IOPA X-Ray",
                warranty_terms="5 Year Crown Warranty"
            ),
            ProcedureCatalog(
                name="Dental Implant Placement",
                category="Implantology",
                duration_minutes=60,
                price_min=Decimal("25000.00"),
                price_max=Decimal("45000.00"),
                is_surgical=True,
                prerequisites="CBCT 3D Bone Scan",
                warranty_terms="Lifetime Nobel Biocare Implant Warranty"
            )
        ]
        for p in procedures:
            session.add(p)

        triage_rules = [
            ClinicalTriageRule(
                symptom_keyword="knocked out tooth",
                urgency_level="CRITICAL_EMERGENCY",
                first_aid_instructions="Store tooth in cold milk or saline immediately! Do NOT touch root! Reach clinic within 60 mins!"
            ),
            ClinicalTriageRule(
                symptom_keyword="khoon nikal raha hai",
                urgency_level="CRITICAL_EMERGENCY",
                first_aid_instructions="Apply firm pressure with clean gauze or tea bag for 30 minutes. Keep head elevated!"
            ),
            ClinicalTriageRule(
                symptom_keyword="दांत निकल गया",
                urgency_level="CRITICAL_EMERGENCY",
                first_aid_instructions="दांत को दूध में रखें। तुरंत 60 मिनट के अंदर क्लिनिक आएं!"
            )
        ]
        for tr in triage_rules:
            session.add(tr)

        session.commit()
        logger.info("SQLite Knowledge Base successfully seeded!")


def seed_knowledge_base():
    """Alias for seed_database."""
    seed_database()


if __name__ == "__main__":
    seed_database()
