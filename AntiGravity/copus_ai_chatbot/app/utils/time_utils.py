# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — IST Timezone Utility Engine

from datetime import datetime
from zoneinfo import ZoneInfo

# Strict Indian Standard Time Zone Constant
IST = ZoneInfo("Asia/Kolkata")


def get_current_ist() -> datetime:
    """Returns current datetime in Indian Standard Time (IST)."""
    return datetime.now(IST)


def format_ist_time(dt: datetime) -> str:
    """Formats datetime to user-friendly IST string (e.g., '28 Jul 2026, 04:45 PM IST')."""
    return dt.astimezone(IST).strftime("%d %b %Y, %I:%M %p IST")
