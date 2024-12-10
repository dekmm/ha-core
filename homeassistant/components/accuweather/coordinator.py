"""The AccuWeather coordinator."""

from asyncio import timeout
from collections import defaultdict
from datetime import timedelta, datetime
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
    """Class to manage fetching AccuWeather data API and database."""

    def __init__(
        self,
        hass: HomeAssistant,
        accuweather: AccuWeatherExt,
        name: str,
        coordinator_type: str,
        update_interval: timedelta,
        index_data_store: AccuWeatherIndexGroupDataStore,
        index_id: IndexGroup,
        index_range: IndexRange = IndexRange.FIVE_DAYS,
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
        """Update data via API and database, merging results."""
        try:
            _LOGGER.debug(
                "Fetching API data for index ID: %s, range: %s",
                self.index_id,
                self.index_range,
            )
            async with timeout(10):
                api_data = await self.accuweather.async_get_index_group_data(
                    self.index_id, self.index_range
                )

            _LOGGER.debug("Fetched API data: %s", api_data)

            # Insert API data into the database
            if TYPE_CHECKING:
                assert self.location_key is not None

            for day in api_data:
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

            # Fetch data from the database for the last five days
            database_data = await self._fetch_database_data()

            # Transform database data to match API data format
            formatted_database_data = self._format_database_data(database_data)

            # Merge API and database data
            merged_data = self._merge_data(api_data, formatted_database_data)

            _LOGGER.debug("Merged data: %s", merged_data)

            return merged_data

        except EXCEPTIONS as error:
            _LOGGER.error("Error fetching data: %s", error)
            raise UpdateFailed(error) from error

    async def _fetch_database_data(self) -> list[dict[str, dict[str, Any]]]:
        """Fetch the last five days of data from the database."""
        try:
            today = datetime.now()
            start_date = (today - timedelta(days=5)).strftime("%Y-%m-%d")
            end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")

            database_data = await self.index_data_store.async_query_data_range(
                self.location_key, start_date, end_date
            )

            _LOGGER.debug("Fetched database data: %s", database_data)
            return database_data
        except Exception as e:
            _LOGGER.error("Failed to fetch database data: %s", e)
            return []

    @staticmethod
    def _format_database_data(
        database_data: list[dict[str, Any]],
    ) -> list[dict[str, dict[str, Any]]]:
        """Transform database data to match the API data structure."""
        formatted_data = defaultdict(dict)
        for entry in database_data:
            date = entry["LocalDateTime"]
            index_group = entry["index_group"]
            formatted_data[date][index_group] = {
                "Value": entry["Value"],
                "Category": entry["Category"],
                "CategoryValue": entry["CategoryValue"],
                "Text": entry["Text"],
                "LocalDateTime": date,
            }

        # Convert to a list of dicts, one per day
        return [day_data for day_data in formatted_data.values()]

    @staticmethod
    def _merge_data(
        api_data: list[dict[str, dict[str, Any]]],
        database_data: list[dict[str, dict[str, Any]]],
    ) -> list[dict[str, dict[str, Any]]]:
        """Merge API and database data, prioritizing API data."""
        merged_data = []

        database_data_by_date = {
            list(day.values())[0]["LocalDateTime"]: day for day in database_data
        }

        for api_day in api_data:
            # Extract the date from the API day
            date = list(api_day.values())[0]["LocalDateTime"]
            merged_day = api_day.copy()

            # Add data from database if it exists for this date
            if date in database_data_by_date:
                for key, value in database_data_by_date[date].items():
                    if key not in merged_day:
                        merged_day[key] = value

            merged_data.append(merged_day)

        # Include any additional database data for dates not in the API data
        api_dates = {list(day.values())[0]["LocalDateTime"] for day in api_data}
        for date, db_day in database_data_by_date.items():
            if date not in api_dates:
                merged_data.append(db_day)

        return merged_data


# class AccuWeatherIndexGroupDataUpdateCoordinator(
#     TimestampDataUpdateCoordinator[list[dict[str, dict[str, Any]]]]
# ):
#     """Class to manage fetching AccuWeather data API and database."""

#     def __init__(
#         self,
#         hass: HomeAssistant,
#         accuweather: AccuWeatherExt,
#         name: str,
#         coordinator_type: str,
#         update_interval: timedelta,
#         index_data_store: AccuWeatherIndexGroupDataStore,
#         index_id: IndexGroup,
#         index_range: IndexRange = IndexRange.ONE_DAY,
#     ) -> None:
#         """Initialize."""
#         self.accuweather = accuweather
#         self.location_key = accuweather.location_key

#         if TYPE_CHECKING:
#             assert self.location_key is not None

#         self.device_info = _get_device_info(self.location_key, name)

#         self.index_id = index_id
#         self.index_range = index_range
#         self.index_data_store = index_data_store

#         super().__init__(
#             hass,
#             _LOGGER,
#             name=f"{name} ({coordinator_type})",
#             update_interval=update_interval,
#         )

#     async def _async_update_data(self) -> list[dict[str, dict[str, Any]]]:
#         """Update data via library."""
#         try:
#             _LOGGER.debug(
#                 "Starting data fetch for index ID: %s, range: %s",
#                 self.index_id,
#                 self.index_range,
#             )

#             async with timeout(10):
#                 result = await self.accuweather.async_get_index_group_data(
#                     self.index_id, self.index_range
#                 )

#             _LOGGER.debug("Fetched API data: %s", result)

#             if TYPE_CHECKING:
#                 assert self.location_key is not None

#             for day in result:
#                 _LOGGER.debug("Processing data for day: %s", day)
#                 for index, data in day.items():
#                     _LOGGER.debug("Index: %s, Data: %s", index, data)
#                     await self.index_data_store.async_insert_data(
#                         self.location_key,
#                         index,
#                         data["Value"],
#                         data["Category"],
#                         data["CategoryValue"],
#                         data["LocalDateTime"],
#                         data["Text"],
#                     )
#                     _LOGGER.debug("Inserted data for index: %s", index)

#         except EXCEPTIONS as error:
#             _LOGGER.error("Error fetching data: %s", error)
#             raise UpdateFailed(error) from error

#         _LOGGER.debug("Requests remaining: %d", self.accuweather.requests_remaining)
#         return result


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
