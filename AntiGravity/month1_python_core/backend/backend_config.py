import os
from typing import Dict, Any

API_KEY_HEADER_NAME: str = "X-API-KEY"
TENANT_ID_HEADER_NAME: str = "X-Tenant-ID"

# Default Security Environment Settings
DEFAULT_API_KEY: str = os.getenv("CENTAUR_API_KEY", "centaur_secret_api_key_2026")
DEFAULT_TENANT_ID: str = os.getenv("CENTAUR_TENANT_ID", "clinic_koramangala_001")


def validate_api_key(api_key: str) -> bool:
    """Validates incoming API key for administrative endpoints."""
    if not api_key:
        return False
    return api_key == DEFAULT_API_KEY
