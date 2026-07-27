# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Tier 1 Essential Strategy Handler

from datetime import datetime
from typing import Dict, Callable

from app.services.session.models import PatientSession, CommandResult, ActionType
from app.services.session.base_strategy import AbstractTierStrategy
from app.services.tier_config import SaaSPlanTier


class Tier1Strategy(AbstractTierStrategy):
    """Tier 1 Essential Strategy: 24/7 Digital Receptionist with Live Clock and Safety Rules."""

    def __init__(self):
        super().__init__(SaaSPlanTier.TIER_1)

    def _build_dispatcher_map(self) -> Dict[str, Callable[[PatientSession, str], CommandResult]]:
        return {
            "1. Doctor Details": self._handle_doctor_details,
            "2. Clinic Timings & Live Status": self._handle_timings_status,
            "3. Location & Valet Parking": self._handle_location_parking,
            "4. Cost Ranges & Pricing Sheet": self._handle_cost_ranges,
            "5. Sterilization & Safety Protocols": self._handle_sterilization,
            "6. Patient Reviews": self._handle_reviews,
            "7. 🚨 Dental Emergency (Call Now)": self._handle_emergency_call,
            "8. Exit Session": self._handle_exit
        }

    # --- Dispatcher Handler Methods ---

    def _handle_doctor_details(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "👨‍⚕️ *Lead Surgeon & Specialist*: Dr. Chinmay Hudedamani (MDS, Oral & Maxillofacial Surgery)\n"
            "• 12+ Years Clinical Excellence\n"
            "• Specialized in Microscopic RCT & Permanent Dental Implants\n"
            "• Yelahanka Node v0.2 & Koramangala Main Branch"
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_timings_status(self, session: PatientSession, option_text: str) -> CommandResult:
        # Dynamic IST Status Clock Calculation
        now = datetime.now()
        hour = now.hour
        is_open = 9 <= hour < 20  # Open 09:00 AM to 08:30 PM IST
        status_str = "🟢 OPEN NOW (Mon-Sat 09:00 AM - 08:30 PM)" if is_open else "🔴 CLOSED NOW (Reopens Mon 09:00 AM)"

        body = (
            f"🕒 *CLINIC LIVE STATUS*: {status_str}\n\n"
            f"• Mon-Sat: 09:00 AM – 08:30 PM\n"
            f"• Sunday: 10:00 AM – 02:00 PM (Emergency Only)"
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_location_parking(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "📍 *LOCATION & PARKING*:\n"
            "5th Phase, Yelahanka New Town, Bengaluru (near Major Sandeep Unnikrishnan Road).\n"
            "🚗 *Valet Parking*: Free Basement Valet Parking available on site!"
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_cost_ranges(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "💰 *ESTIMATED COST RANGES*:\n"
            "• General Consultation: ₹700\n"
            "• Microscopic Root Canal (RCT): ₹4,500 – ₹7,500\n"
            "• Dental Implants: ₹25,000 – ₹45,000\n"
            "• Clear Aligners / Braces: ₹30,000 – ₹70,000"
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_sterilization(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "🛡️ *STERILIZATION & SAFETY PROTOCOLS*:\n"
            "• Class-B German Autoclave 6-Step Sterilization\n"
            "• 100% Disinfected & Single-Use Disposable Pouch Kits\n"
            "• ISO 9001 Certified Clinical Environment"
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_reviews(self, session: PatientSession, option_text: str) -> CommandResult:
        body = (
            "⭐ *PATIENT REVIEWS & RATINGS*:\n"
            "• Google Rating: 4.9 / 5.0 (1,200+ Verified Patient Reviews)\n"
            "• 'Dr. Chinmay is incredibly gentle and painless!' — Ananya R."
        )
        return self._handle_informational_option(session, option_text, body)

    def _handle_emergency_call(self, session: PatientSession, option_text: str) -> CommandResult:
        msg = (
            "🚨 *24/7 DENTAL EMERGENCY LINE*\n"
            "Tap to call our emergency desk directly: tel:+919876543210\n"
            "Or head directly to Yelahanka New Town 5th Phase!"
        )
        return CommandResult(
            success=True,
            message=msg,
            action_type=ActionType.EMERGENCY,
            payload={"tel_uri": "tel:+919876543210"}
        )

    def _handle_exit(self, session: PatientSession, option_text: str) -> CommandResult:
        session.is_active = False
        return CommandResult(
            success=True,
            message="👋 Thank you for contacting APEX Dental. Session closed.",
            action_type=ActionType.NAVIGATION
        )
