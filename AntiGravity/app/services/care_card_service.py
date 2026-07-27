# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# Copus AI / APEX AI — Post-Consultation Digital Care Card Generator

from typing import Dict, Any

CARE_GUIDELINES: Dict[str, Dict[str, Any]] = {
    "EXTRACTION": {
        "title": "🦷 Tooth Extraction Post-Op Care Card",
        "dos": [
            "Bite firmly on clean gauze for 45 minutes post-procedure.",
            "Apply ice pack externally to cheek (15 mins on / 15 mins off).",
            "Stick to soft, cold foods (ice cream, yogurt, cold soup) for 24 hours."
        ],
        "donts": [
            "Do NOT spit, rinse vigorously, or use a drinking straw for 24 hours.",
            "Do NOT consume hot beverages, alcohol, or smoke for 48 hours."
        ]
    },
    "ROOT_CANAL": {
        "title": "🔬 Microscopic Root Canal Care Card",
        "dos": [
            "Take prescribed anti-inflammatory medication as instructed by Dr. Chinmay.",
            "Rinse gently with warm salt water 24 hours after treatment.",
            "Chew on the opposite side until final permanent crown placement."
        ],
        "donts": [
            "Do NOT chew hard objects (ice, hard candy) on the treated tooth.",
            "Do NOT skip your final crown fitting appointment!"
        ]
    },
    "ALIGNERS": {
        "title": "✨ Clear Aligners Care Card",
        "dos": [
            "Wear aligners for 20-22 hours daily for optimal movement.",
            "Clean aligners with lukewarm water and soft toothbrush daily.",
            "Store aligners safely in protective case when eating."
        ],
        "donts": [
            "Do NOT drink hot tea/coffee or sugary drinks with aligners in place.",
            "Do NOT use harsh toothpaste or hot water to sanitize aligners."
        ]
    },
    "GENERAL": {
        "title": "🌿 General Dental Routine Care Card",
        "dos": [
            "Brush twice daily with fluoridated toothpaste.",
            "Floss daily between all interdental spaces.",
            "Schedule regular 6-month check-ups & professional cleaning."
        ],
        "donts": [
            "Do NOT use teeth to open packages or bottle caps.",
            "Do NOT ignore early signs of bleeding gums or sensitivity."
        ]
    }
}


def send_post_care_card(patient_phone: str, procedure_type: str = "GENERAL") -> str:
    """Generates structured digital post-care guidelines with emergency contact and recall link."""
    key = procedure_type.upper()
    data = CARE_GUIDELINES.get(key, CARE_GUIDELINES["GENERAL"])

    dos_str = "\n".join([f"  ✅ {item}" for item in data["dos"]])
    donts_str = "\n".join([f"  ❌ {item}" for item in data["donts"]])

    card = (
        f"📋 *{data['title']}*\n"
        f"Recipient: {patient_phone}\n\n"
        f"*RECOMMENDED DO'S*:\n{dos_str}\n\n"
        f"*IMPORTANT DON'TS*:\n{donts_str}\n\n"
        f"🚨 *24/7 Emergency Line*: Call +91-7338350871\n"
        f"📅 *Schedule Next Recall*: https://kasthuridental.com/recall?phone={patient_phone}"
    )

    return card
