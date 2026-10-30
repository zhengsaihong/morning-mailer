"""
Synthetic data payloads for DEMO_MODE.

Used when DAILYBRIEFING_DEMO=1 to render a sample briefing without any
live API calls, credentials, or Gmail send. Keeps all the fake data in
one file so the main script stays clean.

The screenshot embedded in README.md is generated from these values.
"""

DEMO_WEATHER = {
    "temp":         68,
    "feels_like":   66,
    "conditions":   "Partly cloudy",
    "condition_id": 802,
    "wind_spd":     8,
    "wind_dir":     "NW",
    "high":         75,
    "low":          55,
    "alerts":       [],
}

DEMO_GREETING = (
    "Good morning, Corey — looks like a mild, partly-cloudy Thursday. "
    "Solid day for deep work."
)

DEMO_CALENDAR_EVENTS = [
    {"time_str": "09:00 AM", "summary": "Leadership staff meeting",  "label": "Personal"},
    {"time_str": "11:30 AM", "summary": "1:1 with advisor",          "label": "Personal"},
    {"time_str": "02:30 PM", "summary": "Quarterly vendor review",   "label": "Personal"},
    {"time_str": "05:30 PM", "summary": "Kids' soccer practice",     "label": "Family"},
]

DEMO_TASKS = {
    "active": [
        {"text": "Finalize Q2 infrastructure budget review",     "overdue": False},
        {"text": "Draft incident postmortem for March outage",   "overdue": False},
        {"text": "Schedule quarterly check-in with MSP partner", "overdue": False},
        {"text": "Submit expense report for conference travel",  "overdue": False},
    ],
    "waiting": [],
}
