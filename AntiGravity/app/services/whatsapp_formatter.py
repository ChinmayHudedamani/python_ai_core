# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# Copus AI / APEX AI — Meta WhatsApp API Constraint Sanitizer

from typing import List, Dict, Any


class WhatsAppFormatter:
    """Helper class enforcing Meta WhatsApp Cloud API UI rendering payload constraints."""

    @staticmethod
    def format_menu(options: List[str]) -> Dict[str, Any]:
        """Formats menu options based on Meta WhatsApp limits:
        - len <= 3: Quick Reply Buttons
        - 3 < len <= 10: Interactive List Menu
        - len > 10: Truncated to 9 items + Next Page button
        """
        if not options:
            return {"type": "text", "body": "No menu options available."}

        # Rule: len > 10 requires pagination
        if len(options) > 10:
            truncated = options[:9]
            truncated.append("10. ➡️ Next Page")
            options = truncated

        # Rule: <= 3 items render as Quick Reply Buttons
        if len(options) <= 3:
            return {
                "type": "quick_reply_buttons",
                "buttons": [{"id": f"btn_{i+1}", "title": opt[:20]} for i, opt in enumerate(options)],
                "options": options
            }

        # Rule: 3 < len <= 10 renders as Interactive List Menu
        return {
            "type": "interactive_list_menu",
            "button_text": "Select Option",
            "sections": [
                {
                    "title": "Available Services & Actions",
                    "rows": [{"id": f"row_{i+1}", "title": opt[:24]} for i, opt in enumerate(options)]
                }
            ],
            "options": options
        }
