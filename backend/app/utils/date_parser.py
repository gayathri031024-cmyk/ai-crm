"""
Best-effort natural-language date resolution. The agent's system prompt
instructs the model to resolve phrases like "today" or "next Friday" into
ISO dates itself, but this is a safety net in case it doesn't.
"""
import re
from datetime import date, datetime, timedelta

WEEKDAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}


def resolve_date_phrase(phrase: str | None, reference: date | None = None) -> str | None:
    """Returns an ISO date string (YYYY-MM-DD), or None if phrase is None/unparseable."""
    if not phrase:
        return None

    ref = reference or datetime.utcnow().date()
    text = phrase.strip().lower()

    # Already ISO-ish (e.g. "2026-07-20" or a full datetime string)
    iso_match = re.match(r"^\d{4}-\d{2}-\d{2}", text)
    if iso_match:
        return iso_match.group(0)

    if text in ("today",):
        return ref.isoformat()
    if text in ("tomorrow",):
        return (ref + timedelta(days=1)).isoformat()

    next_match = re.match(r"^next\s+(\w+)$", text)
    if next_match and next_match.group(1) in WEEKDAYS:
        target = WEEKDAYS[next_match.group(1)]
        days_ahead = (target - ref.weekday() + 7) % 7
        days_ahead = days_ahead + 7 if days_ahead == 0 else days_ahead
        return (ref + timedelta(days=days_ahead)).isoformat()

    if text in WEEKDAYS:
        target = WEEKDAYS[text]
        days_ahead = (target - ref.weekday() + 7) % 7
        days_ahead = days_ahead if days_ahead != 0 else 7
        return (ref + timedelta(days=days_ahead)).isoformat()

    # Give up gracefully — let Pydantic validation surface the bad value
    return phrase
