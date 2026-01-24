"""
email.audit — Black Box Validator

Enforces: Axiom 2 (Audit Trail)
Trigger: before_send

Every email MUST be logged before transmission.
"""

from datetime import datetime
from pathlib import Path
import json

VERSION = "1.0.0"
VALIDATOR_ID = "email.audit"


def validate(context: dict) -> dict:
    """
    Black box validation.

    Input: context with to, subject, body, timestamp
    Output: {"status": "pass|fail|warn", "reason": str}
    """
    # Validate required fields exist
    required = ["to", "subject", "timestamp"]
    for field in required:
        if field not in context or not context[field]:
            return {"status": "fail", "reason": f"Missing required field: {field}"}

    # Validate timestamp is ISO format
    try:
        datetime.fromisoformat(context["timestamp"].replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return {"status": "fail", "reason": "Invalid timestamp format"}

    # Validate audit log directory exists
    sent_dir = Path(__file__).parent.parent / "sent"
    if not sent_dir.exists():
        return {"status": "fail", "reason": "Audit directory does not exist"}

    return {"status": "pass", "reason": "Audit trail ready"}


def log_send(context: dict, sent_dir: Path) -> Path:
    """Create audit log entry. Returns log file path."""
    timestamp = datetime.utcnow()
    log_entry = {
        "validator": VALIDATOR_ID,
        "version": VERSION,
        "timestamp": timestamp.isoformat() + "Z",
        "to": context["to"],
        "subject": context["subject"],
        "status": "sent",
        "outlook": True
    }

    recipient_prefix = context["to"].split("@")[0][:20]
    log_file = sent_dir / f"{timestamp.strftime('%Y%m%d-%H%M%S')}-{recipient_prefix}.json"
    log_file.write_text(json.dumps(log_entry, indent=2))

    return log_file
