"""Newly authored fictional inputs only; no gold, held-out cases, or expected answers."""

from .workspace_contracts import DevelopmentCase

DEVELOPMENT_CASES = (
    DevelopmentCase(
        id="demo-101",
        title="Appointment confirmation",
        text="Caller: I received the appointment details. That answers my question.\n"
        "Representative: Glad we could clear that up.\n"
        "Caller: Please still call me tomorrow to confirm the time with my sister.\n"
        "Representative: I have noted your request.\nCaller: Thank you. Goodbye.",
    ),
    DevelopmentCase(
        id="demo-102",
        title="Directions clarified",
        text="Caller: I could not find your entrance.\n"
        "Representative: Use the east entrance, beside the pharmacy.\n"
        "Caller: I see it now. That solves it and I do not need any further help.\n"
        "Representative: See you shortly.",
    ),
    DevelopmentCase(
        id="demo-103",
        title="Call ends mid-request",
        text="Caller: I am calling about the forms you sent. I need to ask whether…\n"
        "[Conversation ends before the request is completed.]",
    ),
)
