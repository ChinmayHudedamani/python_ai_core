import datetime
from pathlib import Path
from typing import Dict, Any

CALENDAR_DIR: Path = Path(__file__).parent / "calendar_events"

def ensure_calendar_dir() -> None:
    CALENDAR_DIR.mkdir(parents=True, exist_ok=True)


class ICalAppointmentGenerator:
    """
    Generates standard 1-Click .ics iCal / Google Calendar Event Files for Dental Consultations.
    """

    def __init__(self):
        ensure_calendar_dir()

    def create_ics_event(self, patient_name: str, procedure_name: str, doctor_name: str, slot_time_str: str) -> str:
        """
        Creates a valid .ics calendar invitation file.
        Returns the absolute filepath of the generated event file.
        """
        now: datetime.datetime = datetime.datetime.now()
        dt_start: str = now.strftime("%Y%m%dT110000Z")
        dt_end: str = now.strftime("%Y%m%dT120000Z")

        ics_content: str = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Apex Dental Centaur//Appointment System//EN
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
UID:apt-{now.strftime('%Y%m%d%H%M%S')}@apexdental.in
DTSTAMP:{now.strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{dt_start}
DTEND:{dt_end}
SUMMARY:🦷 Dental Consultation: {procedure_name} - Apex Dental
DESCRIPTION:Consultation for {patient_name} with {doctor_name}. Location: Koramangala 100 Ft Rd, Bengaluru.
LOCATION:Apex Dental Centaur, 100 Feet Road, Koramangala, Bengaluru, Karnataka 560034
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR"""

        clean_name: str = patient_name.replace(" ", "_").lower()
        file_path: Path = CALENDAR_DIR / f"appointment_{clean_name}_{now.strftime('%Y%m%d_%H%M%S')}.ics"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(ics_content.strip())

        return str(file_path)


if __name__ == "__main__":
    gen = ICalAppointmentGenerator()
    ics_file = gen.create_ics_event("Ananya Roy", "Invisalign Clear Aligners", "Dr. Chinmay Hudedamani", "Saturday at 11:00 AM")
    print(f"Generated 1-Click iCal event at: {ics_file}")
