import json
import sys
import io
from pathlib import Path
from decimal import Decimal
from typing import Optional

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import SQLModel, Field, create_engine, Session, select
from app.models.kb import (
    ClinicProfile, DoctorProfile, ProcedureCatalog,
    ClinicFAQ, ClinicalTriageRule, CallbackLead
)

# Force UTF-8 stdout encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_FILE = "clinic_kb.db"
engine = create_engine(f"sqlite:///{DB_FILE}", echo=False)


def seed_database():
    print("🌱 Seeding SQLite Relational Knowledge Base (clinic_kb.db)...")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if session.exec(select(ClinicProfile)).first():
            print("ℹ️ Database already seeded. Skipping.")
            return

        session.add(ClinicProfile(
            name="APEX Dental & Maxillofacial Centre",
            address="102, 1st Floor, Indiranagar Double Road, Above HDFC Bank, Indiranagar, Bengaluru, Karnataka 560038",
            landmark="Opposite Metro Pillar 42, Above HDFC Bank",
            parking_info="Free dedicated basement parking available for patients (Valet service available on weekdays).",
            operating_hours=json.dumps({"Monday_to_Saturday": "09:30 AM - 08:30 PM", "Sunday": "10:00 AM - 02:00 PM (Prior Appt Only)"}),
            online_consult_available=True,
            accepted_payments="UPI (GPay/PhonePe), Credit/Debit Cards, Cash, No-Cost EMI via Bajaj Finserv"
        ))

        session.add_all([
            DoctorProfile(name="Dr. Vikram Sharma", title="Lead Endodontist & Micro-Surgeon", qualifications="BDS, MDS (Endodontics)", experience_years=14, bio="Specialist in single-sitting painless root canals.", specialties=json.dumps(["Root Canal Treatment", "Painless RCT", "Dental Trauma"]), consultation_fee=Decimal("700.00"), available_days="Monday, Tuesday, Thursday, Friday, Saturday"),
            DoctorProfile(name="Dr. Rajesh Nair", title="Consultant Implantologist & Oral Surgeon", qualifications="BDS, MDS (Oral & Maxillofacial Surgery)", experience_years=16, bio="Pioneer in immediate loading dental implants.", specialties=json.dumps(["Dental Implants", "Wisdom Tooth Surgery", "Full Mouth Reconstruction"]), consultation_fee=Decimal("1000.00"), available_days="Monday, Wednesday, Thursday, Saturday")
        ])

        session.add_all([
            ProcedureCatalog(name="Microscopic Single-Sitting Root Canal (RCT)", category="Endodontics", price_min=Decimal("4500.00"), price_max=Decimal("8500.00"), duration_minutes=60, is_surgical=False, prerequisites="Digital IOPA or OPG X-Ray required (₹300 - ₹500).", warranty_terms="N/A"),
            ProcedureCatalog(name="Korean/Swiss Dental Implant", category="Implantology", price_min=Decimal("25000.00"), price_max=Decimal("60000.00"), duration_minutes=90, is_surgical=True, prerequisites="CBCT 3D Bone Scan (₹2,500) mandatory prior to surgery.", warranty_terms="Lifetime Warranty on Titanium Implant Fixture"),
            ProcedureCatalog(name="Invisalign® Clear Aligners", category="Orthodontics", price_min=Decimal("140000.00"), price_max=Decimal("275000.00"), duration_minutes=45, is_surgical=False, prerequisites="3D iTero Digital Intraoral Scan required.", warranty_terms="Includes up to 3 refinement sets within 5 years"),
            ProcedureCatalog(name="Surgical Wisdom Tooth Extraction", category="Oral Surgery", price_min=Decimal("4000.00"), price_max=Decimal("9500.00"), duration_minutes=60, is_surgical=True, prerequisites="Mandatory IOPA/OPG X-ray. Post-op soft diet required for 48 hours.", warranty_terms="N/A")
        ])

        session.add_all([
            ClinicalTriageRule(symptom_keyword="knocked out tooth", urgency_level="CRITICAL_EMERGENCY", first_aid_instructions="Place the knocked-out tooth in a small container of cold milk or saliva—do NOT scrub the root! Bypass standard booking and alert doctor immediately."),
            ClinicalTriageRule(symptom_keyword="uncontrolled bleeding", urgency_level="CRITICAL_EMERGENCY", first_aid_instructions="Bite down firmly on a clean gauze pad. Alert emergency desk immediately."),
            ClinicalTriageRule(symptom_keyword="swelling extending to neck", urgency_level="CRITICAL_EMERGENCY", first_aid_instructions="Head to the clinic immediately. Severe space infections require urgent attention."),
            ClinicalTriageRule(symptom_keyword="throbbing pain preventing sleep", urgency_level="SAME_DAY_URGENT", first_aid_instructions="Take an over-the-counter pain reliever if not contraindicated. Let's find you an immediate slot.")
        ])

        session.commit()
        print("✅ SQLite Knowledge Base successfully populated!")


if __name__ == "__main__":
    seed_database()
