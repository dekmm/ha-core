"""The AccuWeather coordinator."""

from asyncio import timeout
from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any

from accuweather import ApiError, InvalidApiKeyError, RequestsExceededError
from aiohttp.client_exceptions import ClientConnectorError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    TimestampDataUpdateCoordinator,
    UpdateFailed,
)

from .api import AccuWeatherExt, IndexGroup, IndexRange
from .const import DOMAIN, MANUFACTURER
from .db import AccuWeatherIndexGroupDataStore

EXCEPTIONS = (ApiError, ClientConnectorError, InvalidApiKeyError, RequestsExceededError)

_LOGGER = logging.getLogger(__name__)


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
        index_data_store: AccuWeatherIndexGroupDataStore,
        index_id: IndexGroup,
        index_range: IndexRange = IndexRange.ONE_DAY,
    ) -> None:
        """Initialize."""
        self.accuweather = accuweather
        self.location_key = accuweather.location_key

        if TYPE_CHECKING:
            assert self.location_key is not None

        self.device_info = _get_device_info(self.location_key, name)

        self.index_id = index_id
        self.index_range = index_range
        self.index_data_store = index_data_store

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
                    self.index_id, self.index_range
                )

                if TYPE_CHECKING:
                    assert self.location_key is not None

                for day in result:
                    for index, data in day.items():
                        await self.index_data_store.async_insert_data(
                            self.location_key,
                            index,
                            data["Value"],
                            data["Category"],
                            data["CategoryValue"],
                            data["LocalDateTime"],
                            data["Text"],
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


class AccuWeatherLocationDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for fetching AccuWeather location details."""

    def __init__(
        self,
        hass: HomeAssistant,
        accuweather: AccuWeatherExt,
        name: str,
        update_interval: timedelta,
    ) -> None:
        """Initialize the location coordinator."""
        self.accuweather = accuweather
        self.location_key = accuweather.location_key
        self.city = "Unknown City"
        self.country = "Unknown Country"

        if TYPE_CHECKING:
            assert self.location_key is not None

        self.device_info = _get_device_info(self.location_key, name)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{name} (location)",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch location details from AccuWeather."""
        try:
            async with timeout(10):
                location_details = await self.accuweather.async_get_location_details()
        except EXCEPTIONS as error:
            raise UpdateFailed(error) from error

        _LOGGER.debug("Fetched location details: %s", location_details)

        # Extract city and country from the response
        self.city = location_details.get("city", "Unknown City")
        self.country = location_details.get("country", "Unknown Country")

        return location_details

    @property
    def location_info(self) -> dict[str, str]:
        """Return location information."""
        return {"city": self.city, "country": self.country}


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
