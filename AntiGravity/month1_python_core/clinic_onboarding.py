import json
import sys
from pathlib import Path
from typing import Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

KB_PATH: Path = Path(__file__).parent / "clinic_knowledge_base.json"

def customize_clinic_onboarding(clinic_name: str, doctor_name: str, phone: str, location: str) -> None:
    """Configures clinic details in knowledge base for new doctor deployment."""
    kb_data: Dict[str, Any] = {}
    if KB_PATH.exists():
        with open(KB_PATH, "r", encoding="utf-8") as f:
            kb_data = json.load(f)

    clinic_info = kb_data.get("clinic_info", {})
    clinic_info["name"] = clinic_name.strip()
    clinic_info["contact_phone"] = phone.strip()
    clinic_info["location"] = location.strip()
    kb_data["clinic_info"] = clinic_info

    doctors = kb_data.get("doctors", [])
    if doctors:
        doctors[0]["name"] = doctor_name.strip()
    else:
        doctors.append({"name": doctor_name.strip(), "specialty": "Senior Dental Specialist & Implantologist", "qualification": "MDS"})
    kb_data["doctors"] = doctors

    with open(KB_PATH, "w", encoding="utf-8") as f:
        json.dump(kb_data, f, indent=2)

    print(f"\n✅ CLINIC ONBOARDING COMPLETE FOR: {clinic_name}")
    print(f"   • Attending Specialist: {doctor_name}")
    print(f"   • Doctor Phone Alert  : {phone}")
    print(f"   • Clinic Location     : {location}\n")


if __name__ == "__main__":
    print("==================================================")
    print(" 🏥 CENTAUR CLINIC DESKTOP ONBOARDING WIZARD")
    print("==================================================\n")
    c_name = input("1. Clinic Name [e.g. Apex Dental Center]: ").strip() or "Apex Dental Center"
    d_name = input("2. Chief Doctor Name [e.g. Dr. Chinmay Hudedamani]: ").strip() or "Dr. Chinmay Hudedamani"
    phone = input("3. Doctor WhatsApp Number [e.g. +91-9988776655]: ").strip() or "+91-9988776655"
    location = input("4. Clinic Location [e.g. Koramangala 100 Ft Rd, Bengaluru]: ").strip() or "Koramangala 100 Ft Rd, Bengaluru"

    customize_clinic_onboarding(c_name, d_name, phone, location)
