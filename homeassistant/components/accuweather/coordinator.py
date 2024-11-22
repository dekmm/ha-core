"""The AccuWeather coordinator."""

from asyncio import timeout
from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any

from accuweather import ApiError, InvalidApiKeyError, RequestsExceededError
from aiohttp.client_exceptions import ClientConnectorError

from homeassistant.components.persistent_notification importasync_create as create_persistent_notification
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    TimestampDataUpdateCoordinator,
    UpdateFailed,
)

from .api import AccuWeatherExt, IndexGroup
from .const import DOMAIN, MANUFACTURER

EXCEPTIONS = (ApiError, ClientConnectorError, InvalidApiKeyError, RequestsExceededError)

_LOGGER = logging.getLogger(__name__)

#  Define the thresholds for health conditions (e.g., arthritis, asthma, etc.)
HEALTH_CONDITION_THRESHOLDS = {
    "arthritis_pain_forecast": ["At Extreme Risk", "At High Risk", "At Risk"],
    "asthma_forecast": ["At Extreme Risk", "At Hight Risk ", "At Risk"],
    "sinus_pressure_forecast": ["At Extreme Risk", "At High Risk"],
    "common_cold_forecast": ["At Extreme Risk", "At High Risk", "At Risk"],
    "flu_forecast": ["At Extreme Risk", "At High Risk", "At Risk"],
    "migraine_headache_forecast": ["At Extreme Risk", "At High Risk", "At Risk"],
}


#  Notification function to send messages to Home Assistant UI
async def send_health_notification(
    hass: HomeAssistant | None, condition: str, value: str
):
    """Send a notification if a health condition is critical."""
    message = f"Health Alert: The condition {condition} is currently {value}. Please take necessary precautions."
    _LOGGER.debug("Attempting to create notification: %s", message)
    await create_persistent_notification(
        hass,
        message=message,
        title="Health Risk Alert",
        notification_id=f"{condition}_alert",
    )
    _LOGGER.debug("Notification created successfully.")

    await create_persistent_notification(
        hass,
        message="Test Notification",
        title="Test",
        notification_id="test_notification",
    )


#  Function to check if any health condition reaches the critical threshold and notify
async def check_and_notify_health_conditions(hass: HomeAssistant, sensor_data: dict):
    _LOGGER.debug("Sensor data: %s", sensor_data)
    """Check sensor values and notify if they exceed critical thresholds."""
    for condition, value in sensor_data.items():
        _LOGGER.debug("Checking condition: %s with value: %s", condition, value)
        # Check if the condition exists in the thresholds and if it meets the critical levels
        if value in HEALTH_CONDITION_THRESHOLDS.get(condition, []):
            _LOGGER.debug(
                "Health condition: %s with value: %s exceeds the threshold",
                condition,
                value,
            )
            # Send notification if the condition is at risk
            await send_health_notification(hass, condition, value)
        else:
            _LOGGER.debug(
                "Health condition: %s with value: %s is within safe limits",
                condition,
                value,
            )


class AccuWeatherObservationDataUpdateCoordinator(
    DataUpdateCoordinator[dict[str, Any]]
):
    """Class to manage fetching AccuWeather data API."""

    def __init__(
        self,
        hass: HomeAssistant,
        accuweather: AccuWeatherExt,
        name: str,
        coordinator_type: str,
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.accuweather = accuweather
        self.location_key = accuweather.location_key

        if TYPE_CHECKING:
            assert self.location_key is not None

        self.device_info = _get_device_info(self.location_key, name)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{name} ({coordinator_type})",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            async with timeout(10):
                result = await self.accuweather.async_get_current_conditions()
        except EXCEPTIONS as error:
            raise UpdateFailed(error) from error

        _LOGGER.debug("Requests remaining: %d", self.accuweather.requests_remaining)

        return result


class AccuWeatherIndexGroupDataUpdateCoordinator(
    TimestampDataUpdateCoordinator[list[dict[str, dict[str, Any]]]]
):
    """Class to manage fetching AccuWeather data API."""

    def __init__(
        self,
        hass: HomeAssistant,
        accuweather: AccuWeatherExt,
        name: str,
        coordinator_type: str,
        update_interval: timedelta,
        index_id: IndexGroup,
    ) -> None:
        """Initialize."""
        self.accuweather = accuweather
        self.location_key = accuweather.location_key

        if TYPE_CHECKING:
            assert self.location_key is not None

        self.device_info = _get_device_info(self.location_key, name)

        self.index_id = index_id

        super().__init__(
            hass,
            _LOGGER,
            name=f"{name} ({coordinator_type})",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> list[dict[str, dict[str, Any]]]:
        """Update data via library."""
        try:
            async with timeout(10):
                result = await self.accuweather.async_get_index_group_data(
                    self.index_id
                )
        except EXCEPTIONS as error:
            raise UpdateFailed(error) from error

        _LOGGER.debug("Requests remaining: %d", self.accuweather.requests_remaining)

        return result


class AccuWeatherDailyForecastDataUpdateCoordinator(
    TimestampDataUpdateCoordinator[list[dict[str, Any]]]
):
    """Class to manage fetching AccuWeather data API."""

    def __init__(
        self,
        hass: HomeAssistant,
        accuweather: AccuWeatherExt,
        name: str,
        coordinator_type: str,
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.accuweather = accuweather
        self.location_key = accuweather.location_key

        if TYPE_CHECKING:
            assert self.location_key is not None

        self.device_info = _get_device_info(self.location_key, name)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{name} ({coordinator_type})",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> list[dict[str, Any]]:
        """Update data via library."""
        try:
            async with timeout(10):
                result = await self.accuweather.async_get_daily_forecast()
        except EXCEPTIONS as error:
            raise UpdateFailed(error) from error

        _LOGGER.debug("Requests remaining: %d", self.accuweather.requests_remaining)

        return result


def _get_device_info(location_key: str, name: str) -> DeviceInfo:
    """Get device info."""
    return DeviceInfo(
        entry_type=DeviceEntryType.SERVICE,
        identifiers={(DOMAIN, location_key)},
        manufacturer=MANUFACTURER,
        name=name,
        # You don't need to provide specific details for the URL,
        # so passing in _ characters is fine if the location key
        # is correct
        configuration_url=(
            "http://accuweather.com/en/"
            f"_/_/{location_key}/weather-forecast/{location_key}/"
        ),
    )
