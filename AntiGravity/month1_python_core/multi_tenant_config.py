import json
from pathlib import Path
from typing import Dict, Any, List, Optional

TENANTS_DIR: Path = Path(__file__).parent / "tenants"

def ensure_tenants_dir() -> None:
    TENANTS_DIR.mkdir(parents=True, exist_ok=True)


class MultiTenantClinicManager:
    """
    Enterprise Multi-Tenant Clinic Configuration & Provisioning Engine.
    Allows scaling the AI Centaur platform across 100+ private dental clinics
    with isolated pricing schema, doctor schedules, and Meta API credentials.
    """

    def __init__(self):
        ensure_tenants_dir()
        self._bootstrap_default_tenants()

    def _bootstrap_default_tenants(self) -> None:
        """Bootstraps sample clinic tenants for investor demonstration."""
        default_tenants: List[Dict[str, Any]] = [
            {
                "tenant_id": "clinic_koramangala_001",
                "clinic_name": "Apex Dental Centaur & Implant Center",
                "city": "Bengaluru",
                "locality": "Koramangala 100 Ft Road",
                "contact_phone": "+91-9988776655",
                "doctor_in_charge": "Dr. Chinmay Hudedamani",
                "specialty": "Dental Implants & Full Mouth Rehab",
                "pricing": {
                    "ALIGNERS": {"min_price": 85000, "max_price": 220000, "emi_monthly": 7500},
                    "IMPLANTS": {"min_price": 35000, "max_price": 95000, "emi_monthly": 4500},
                    "RCT": {"min_price": 6500, "max_price": 18000, "emi_monthly": 0}
                }
            },
            {
                "tenant_id": "clinic_indiranagar_002",
                "clinic_name": "Indiranagar Perfect Smile Studio",
                "city": "Bengaluru",
                "locality": "100 Feet Road, Indiranagar",
                "contact_phone": "+91-9876543210",
                "doctor_in_charge": "Dr. Ananya Roy",
                "specialty": "Orthodontics & Aesthetic Smile Makeovers",
                "pricing": {
                    "ALIGNERS": {"min_price": 90000, "max_price": 250000, "emi_monthly": 8000},
                    "IMPLANTS": {"min_price": 40000, "max_price": 105000, "emi_monthly": 5000},
                    "RCT": {"min_price": 7000, "max_price": 20000, "emi_monthly": 0}
                }
            }
        ]

        for tenant in default_tenants:
            t_file: Path = TENANTS_DIR / f"{tenant['tenant_id']}.json"
            if not t_file.exists():
                with open(t_file, "w", encoding="utf-8") as f:
                    json.dump(tenant, f, indent=2)

    def list_active_tenants(self) -> List[Dict[str, Any]]:
        """Returns all provisioned clinic tenants."""
        tenants: List[Dict[str, Any]] = []
        for t_file in TENANTS_DIR.glob("*.json"):
            try:
                with open(t_file, "r", encoding="utf-8") as f:
                    tenants.append(json.load(f))
            except Exception:
                pass
        return tenants

    def get_tenant_config(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves tenant configuration by ID."""
        t_file: Path = TENANTS_DIR / f"{tenant_id}.json"
        if t_file.exists():
            with open(t_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None


if __name__ == "__main__":
    manager = MultiTenantClinicManager()
    active_tenants = manager.list_active_tenants()
    print(f"Provisioned Enterprise Tenants: {len(active_tenants)}")
