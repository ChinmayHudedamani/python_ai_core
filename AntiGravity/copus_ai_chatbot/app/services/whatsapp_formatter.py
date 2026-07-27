# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Meta WhatsApp Cloud API Payload Constraint Sanitizer

from dataclasses import dataclass, field
from typing import List, Dict, Any, Final


@dataclass(slots=True)
class FormattedMenuPayload:
    """Memory-optimized slots-backed payload container for Meta WhatsApp API rendering."""
    payload_type: str  # QUICK_REPLY_BUTTONS, INTERACTIVE_LIST_MENU, PAGINATED_LIST_MENU, TEXT
    button_text: str
    sections: List[Dict[str, Any]] = field(default_factory=list)
    buttons: List[Dict[str, Any]] = field(default_factory=list)
    options: List[str] = field(default_factory=list)


class WhatsAppFormatter:
    """Helper class enforcing Meta WhatsApp Cloud API UI rendering payload constraints."""

    MAX_QUICK_REPLIES: Final[int] = 3
    MAX_LIST_ITEMS: Final[int] = 10

    @classmethod
    def format_menu(cls, options: List[str]) -> FormattedMenuPayload:
        """Chunks options according to Meta API limits:
        - len <= 3: QUICK_REPLY_BUTTONS
        - 3 < len <= 10: INTERACTIVE_LIST_MENU
        - len > 10: PAGINATED_LIST_MENU (9 items + '10. ➡️ Next Page')
        """
        if not options:
            return FormattedMenuPayload(
                payload_type="TEXT",
                button_text="No Options",
                options=[]
            )

        # Rule: > 10 options requires pagination
        display_options = list(options)
        is_paginated = False
        if len(display_options) > cls.MAX_LIST_ITEMS:
            display_options = display_options[:9]
            display_options.append("10. ➡️ Next Page")
            is_paginated = True

        # Rule: <= 3 items render as QUICK_REPLY_BUTTONS
        if len(display_options) <= cls.MAX_QUICK_REPLIES:
            button_list = [
                {"id": f"btn_{i+1}", "title": opt[:20]}
                for i, opt in enumerate(display_options)
            ]
            return FormattedMenuPayload(
                payload_type="QUICK_REPLY_BUTTONS",
                button_text="Select Option",
                buttons=button_list,
                options=display_options
            )

        # Rule: 3 < len <= 10 renders as INTERACTIVE_LIST_MENU or PAGINATED_LIST_MENU
        rows = [
            {"id": f"row_{i+1}", "title": opt[:24]}
            for i, opt in enumerate(display_options)
        ]
        payload_kind = "PAGINATED_LIST_MENU" if is_paginated else "INTERACTIVE_LIST_MENU"

        return FormattedMenuPayload(
            payload_type=payload_kind,
            button_text="Select Option",
            sections=[{
                "title": "Available Actions",
                "rows": rows
            }],
            options=display_options
        )
