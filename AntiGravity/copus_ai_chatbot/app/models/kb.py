# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI SQLite Knowledge Base Models (SQLModel)

import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class ClinicProfile(SQLModel, table=True):
    __tablename__ = "clinic_profile"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    address: str
    landmark: str
    parking_info: str
    operating_hours: str  # JSON string
    online_consult_available: bool = Field(default=True)
    accepted_payments: str

class DoctorProfile(SQLModel, table=True):
    __tablename__ = "doctor_profile"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    title: str
    qualifications: str
    experience_years: int
    bio: str
    specialties: str  # JSON list
    consultation_fee: Decimal = Field(default=Decimal("500.00"))
    available_days: str

class ProcedureCatalog(SQLModel, table=True):
    __tablename__ = "procedure_catalog"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    category: str = Field(index=True)
    price_min: Decimal
    price_max: Decimal
    duration_minutes: int
    is_surgical: bool = Field(default=False)
    prerequisites: str
    warranty_terms: str

class ClinicFAQ(SQLModel, table=True):
    __tablename__ = "clinic_faq"
    id: Optional[int] = Field(default=None, primary_key=True)
    category: str = Field(index=True)
    question_patterns: str  # JSON list
    approved_answer: str

class ClinicalTriageRule(SQLModel, table=True):
    __tablename__ = "clinical_triage_rule"
    id: Optional[int] = Field(default=None, primary_key=True)
    symptom_keyword: str = Field(index=True)
    urgency_level: str = Field(index=True)  # CRITICAL_EMERGENCY, SAME_DAY_URGENT, ROUTINE
    first_aid_instructions: str

class CallbackLead(SQLModel, table=True):
    __tablename__ = "callback_lead"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    patient_phone: str = Field(index=True)
    patient_name: Optional[str] = Field(default=None)
    reason: str
    status: str = Field(default="PENDING", index=True)  # PENDING, CONTACTED
    created_at: datetime = Field(default_factory=datetime.utcnow)
