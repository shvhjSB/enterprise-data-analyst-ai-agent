"""Structured logging and audit logging.

Enterprise note:
- In production, route logs to your SIEM (Splunk, Datadog, ELK) and include
  request IDs / trace IDs.
- This implementation uses stdlib logging with JSON-like dict payloads.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def audit_log(event: str, payload: Dict[str, Any]) -> None:
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **payload,
    }
    logging.getLogger("audit").info(json.dumps(record, default=str))