import os

import sentry_sdk
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError


def sanitize_event(event, hint):
    """Hide database exception messages, which can contain SQL parameters."""
    exc_info = hint.get("exc_info")
    if exc_info and isinstance(exc_info[1], SQLAlchemyError):
        for exception in event.get("exception", {}).get("values", []):
            exception["value"] = "Détails SQL masqués."
    return event


def initialize_sentry():
    load_dotenv()

    if os.getenv("SENTRY_DSN"):
        sentry_sdk.init(
            send_default_pii=False,
            include_local_variables=False,
            include_source_context=False,
            max_breadcrumbs=0,
            before_send=sanitize_event,
        )
