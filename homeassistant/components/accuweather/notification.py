"""Helper functions for sending notifications."""

import logging
from typing import Any
import uuid

from homeassistant.components.persistent_notification import (
    create as create_notification,
)
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

HEALTH_CONDITION_THRESHOLDS = [
    "At Extreme Risk",
    "At High Risk",
    "At Risk",
    "Poor",
    "Extreme",
    "Very High",
    "High",
]


def send_health_notification(
    hass: HomeAssistant, index_group: str, index: dict[str, Any]
) -> None:
    """Send a notification if a health condition is critical."""

    if index["Category"] not in HEALTH_CONDITION_THRESHOLDS:
        return

    value = str(index["Category"])
    notification_id = f"{index_group.lower().replace(' ', '_')}_{uuid.uuid4()!s}"

    message = f"The {index_group.lower()} is currently {value.lower()}! Please take necessary precautions."
    create_notification(
        hass,
        message=message,
        title="Health Risk Alert",
        notification_id=notification_id,
    )
