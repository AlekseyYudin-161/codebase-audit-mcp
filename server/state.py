"""In-memory storage for the last health report."""

from typing import Any, Optional

from server.models import HealthReport

LAST_REPORT: Optional[dict[str, Any]] = None


def set_last_report(report: HealthReport) -> None:
    """Store last HealthReport as plain dict for resources to read."""
    report_dict = report.model_dump()
    LAST_REPORT = report_dict


def get_last_report() -> Optional[dict[str, Any]]:
    """Return last stored report dict or None if no report yet."""
    return LAST_REPORT

# def clear_last_report() -> None:
#     global LAST_REPORT
#     LAST_REPORT = None