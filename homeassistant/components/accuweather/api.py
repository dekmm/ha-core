"""Client for getting weather and index data from AccueWeather API."""

from collections import defaultdict
from enum import Enum, StrEnum
from http import HTTPStatus
import logging
from typing import TYPE_CHECKING, Any

from accuweather import AccuWeather
from accuweather.exceptions import ApiError, InvalidApiKeyError, RequestsExceededError
import orjson

BASE_URL: str = "https://dataservice.accuweather.com/"

_LOGGER = logging.getLogger(__name__)


class IndexRange(StrEnum):
    """Index range."""

    ONE_DAY = "1day"
    FIVE_DAYS = "5day"
    TEN_DAYS = "10day"  # Need Prime plan
    FIFTEEN_DAYS = "15day"  # Need Elite plan


class Index(Enum):
    """AccuWeather index types."""

    AIR_CONDITIONING_INDEX = 110
    AIR_POLLUTION_INDEX = 108
    AIR_QUALITY_INDEX = -10
    ALLERGY_INDEX = 127
    APPARENT_TEMPERATURE = 134
    ARTHRITIS_PAIN_FORECAST = 21
    ASTHMA_FORECAST = 23
    ASTHMA_AND_LUNG_DISORDER_INDEX = 150
    ATMOSPHERIC_DISPERSION_INDEX = 142
    OUTDOOR_BARBECUE = 24
    BEACH_POOL_FORECAST = 10
    BEACH_INDEX = 128
    BEER_INDEX = 120
    BICYCLING_FORECAST = 4
    ACCULUMEN_BRIGHTNESS_INDEX_FORECAST = 47
    CAR_WASHING_INDEX = 104
    CARWASHING_FORECAST = 51
    CLIMBING_FORECAST = 52
    CLOTHES_DRYING_FORECAST = 50
    CLOTHES_DRYING_INDEX = 107
    CLOTHING_INDEX = 101
    COMMON_COLD_FORECAST = 25
    COMFORT_INDEX = 103
    COMMON_COLD_INDEX_1 = 102
    COMMON_COLD_INDEX_2 = 153
    COMPOSTING_FORECAST = 38
    OUTDOOR_CONCERT_FORECAST = 8
    CONSTRUCTION_FORECAST = 14
    COPD_FORECAST = 44
    DATING_INDEX = 126
    DISCOMFORT_INDEX = 139
    DOG_WALKING_COMFORT_FORECAST = 43
    DRIVING_TRAVEL_INDEX = 40
    DRY_SKIN_FORECAST = 48
    DRYNESS_INDEX = 133
    DUST_DANDER_FORECAST = 18
    HOME_ENERGY_EFFICIENCY_FORECAST = 36
    EXERCISE_INDEX = 125
    FIELD_READINESS_FORECAST = 32
    FISHING_FORECAST = 13
    FISHING_INDEX = 111
    FLIGHT_DELAYS = -3
    FLU_FORECAST = 26
    FOOD_POISONING_INDEX = 136
    PIPE_FREEZE_BURST_INDEX = 141
    FUEL_ECONOMY_FORECAST = 37
    GOLF_WEATHER_FORECAST = 5
    GRASS_GROWING_FORECAST = 33
    GRASS_POLLEN = -11
    HAIR_FRIZZ_FORECAST = 42
    HAIRDRESSING_INDEX = 118
    HEALTHY_HEART_FITNESS_FORECAST = 16
    HEAT_INDEX = 138
    HEAT_SENSITIVITY_INDEX_CHILDREN = 145
    HEAT_SENSITIVITY_INDEX_CONSTRUCTION = 158
    HEAT_SENSITIVITY_INDEX_GENERAL_PUBLIC = 143
    HEAT_SENSITIVITY_INDEX_OUTDOOR_WORKING_ENVIRONMENT = 146
    HEAT_SENSITIVITY_INDEX_ROAD = 157
    HEAT_SENSITIVITY_INDEX_SHIPYARD = 159
    HEAT_SENSITIVITY_INDEX_THE_ELDERLY = 144
    HEAT_SENSITIVITY_INDEX_VULNERABLE_RESIDENTIAL_ENVIRONMENT = 149
    HEAT_SENSITIVITY_INDEX_FARMING = 147
    HEAT_SENSITIVITY_INDEX_GREENHOUSE = 148
    HEAT_STROKE_INDEX = 105
    HIKING_FORECAST = 3
    HUNTING_FORECAST = 20
    HYPERTENSION_INDEX = 132
    INDOOR_ACTIVITY_FORECAST = -2
    INDOOR_PEST_ACTIVITY_FORECAST = 45
    JOGGING_FORECAST = 2
    KITE_FLYING_FORECAST = 9
    KITE_FLYING_INDEX = 121
    MAKEUP_SKINCARE_FORECAST = 49
    MAKEUP_INDEX = 122
    MIGRAINE_HEADACHE_FORECAST = 27
    MOLD = -12
    MOOD_INDEX = 124
    MORNING_EXERCISE_INDEX = 100
    MOSQUITO_ACTIVITY_FORECAST = 17
    LAWN_MOWING_FORECAST = 28
    NIGHTLIFE_INDEX = 119
    OUTDOOR_ACTIVITY_FORECAST = 29
    OUTDOOR_PEST_ACTIVITY_FORECAST = 46
    PINE_POLLEN_LEVELS = 155
    POLLUTION_PREVENTION = 135
    RAGWEED_POLLEN = -13
    ROAD_CONDITIONS_INDEX = 116
    ROWING_INDEX = 114
    RUNNING_FORECAST = 1
    SAILING_FORECAST = 11
    MORNING_SCHOOL_BUS_FORECAST = 35
    SNOW_DAYS_FORECAST = 19
    SHOPPING_FORECAST = 39
    SHOPPING_INDEX = 113
    SHORT_PHRASE = 131
    SINUS_HEADACHE_FORECAST = 30
    SKATEBOARDING_FORECAST = 7
    SKI_WEATHER_FORECAST = 15
    SKIN_SENSITIVITY_INDEX = 152
    SOIL_MOISTURE_FORECAST = 34
    STARGAZING_FORECAST = 12
    STROKE_INDEX = 151
    SUN_PROTECTION_INDEX = 112
    SUNGLASSES_INDEX = 129
    TENNIS_FORECAST = 6
    THIRST_FORECAST_COUNTRY_TIME = 41
    TOURISM_INDEX = 109
    TRAFFIC_INDEX = 115
    FLYING_TRAVEL_INDEX = 31
    TREE_POLLEN_LEVELS = 154
    TREE_POLLEN = -14
    UMBRELLA_INDEX = 117
    UV_INDEX_1 = 140
    UV_INTENSITY_INDEX = 106
    UV_INDEX_2 = -15
    WEED_POLLEN_LEVELS = 156
    WIND_CHILL_INDEX_1 = 123
    WIND_CHILL_INDEX_2 = 137


class IndexGroup(Enum):
    """AccuWeather index groups."""

    ALL = 1
    ACHES_AND_PAINS = 2
    RESPIRATORY = 3
    GARDENING = 4
    ENVIRONMENTAL = 5
    OUTDOOR_LIVING = 6
    BEACH_AND_MARINE = 7
    SPORTSMAN = 8
    FARMING = 9
    HEALTH = 10
    OUTDOOR = 11
    SPORTING = 12
    HOME = 13
    POLLEN = 30
    OPERA_TV = 31
    LIFESTYLE_ALLERGIES = 32
    LIFESTYLE_COLD_AND_FLU = 33
    LIFESTYLE_DRIVING = 34
    LIFESTYLE_LAWN_AND_GARDEN = 35
    LIFESTYLE_ENTERTAINING = 36
    LIFESTYLE_SUN_AND_SAND = 37
    LIFESTYLE_AIR_TRAVEL = 38
    LIFESTYLE_ARTHRITIS = 39
    LIFESTYLE_RESPIRATORY = 40
    LIFESTYLE_ASTRONOMY = 41
    LIFESTYLE_BIKING = 42
    LIFESTYLE_DIY = 43
    LIFESTYLE_EVENTS = 44
    LIFESTYLE_FISHING = 45
    LIFESTYLE_GOLF = 46
    LIFESTYLE_HAIR_DAY = 47
    LIFESTYLE_HIKING = 48
    LIFESTYLE_HOME_ENERGY = 49
    LIFESTYLE_HUNTING = 50
    LIFESTYLE_MIGRAINE = 51
    LIFESTYLE_RUNNING = 52
    LIFESTLYE_SAILING = 53
    LIFESTYLE_SCHOOL_DAY = 54
    LIFESTYLE_SINUS = 55
    LIFESTYLE_SKI = 56
    LIFESTYLE_SNOW_DAYS = 57
    WEB_ALL = 58
    MOSQUITO = 59
    WINTER_CAST = 60
    PEST = 61
    CHINA_INDICES = 100
    KOREAN_INDICES = 102


class AccuWeatherExt(AccuWeather):
    """Class to extend base AccuWeather API."""

    async def async_get_index_data(
        self, index_id: Index, range: IndexRange = IndexRange.ONE_DAY
    ) -> list[dict[str, dict[str, Any]]]:
        """Retrieve index data from AccuWeather."""
        if not self._location_key:
            await self.async_get_location()

        if TYPE_CHECKING:
            assert self._location_key is not None

        url = (
            BASE_URL
            + f"indices/v1/daily/{range.value}/{self._location_key}/{index_id.value}?apikey={self._api_key}&details=true"
        )

        data = await self._async_get_list_data(url)

        return _parse_index_data(data)

    async def async_get_index_group_data(
        self, index_id: IndexGroup, range: IndexRange = IndexRange.ONE_DAY
    ) -> list[dict[str, dict[str, Any]]]:
        """Retrieve index group data from AccuWeather."""
        if not self._location_key:
            await self.async_get_location()

        if TYPE_CHECKING:
            assert self._location_key is not None

        url = (
            BASE_URL
            + f"/indices/v1/daily/{range.value}/{self._location_key}/groups/{index_id.value}?apikey={self._api_key}&details=true"
        )

        data = await self._async_get_list_data(url)
        return _parse_index_data(data)

    async def async_get_location_details(self) -> dict[str, Any]:
        """Fetch location details using the location key."""
        if not self._location_key:
            raise ValueError("Location key is not set.")

        url = f"{BASE_URL}/locations/v1/{self._location_key}?apikey={self._api_key}"
        response = await self._async_get_data(url)
        _LOGGER.debug("Location details API response: %s", response)

        if not isinstance(response, dict):
            raise ApiError(f"Unexpected response format: {response}")

        # Extract key location details
        location_details = {
            "city": response.get("LocalizedName", "Unknown City"),
            "state": response.get("AdministrativeArea", {}).get(
                "LocalizedName", "Unknown State"
            ),
            "country": response.get("Country", {}).get(
                "LocalizedName", "Unknown Country"
            ),
            "region": response.get("Region", {}).get("LocalizedName", "Unknown Region"),
            "timezone": response.get("TimeZone", {}).get("Name", "Unknown Timezone"),
            "latitude": response.get("GeoPosition", {}).get(
                "Latitude", "Unknown Latitude"
            ),
            "longitude": response.get("GeoPosition", {}).get(
                "Longitude", "Unknown Longitude"
            ),
        }

        _LOGGER.info(
            "Location Details Fetched: City: %s, State: %s, Country: %s, Region: %s, Timezone: %s, Coordinates: (%s, %s)",
            location_details["city"],
            location_details["state"],
            location_details["country"],
            location_details["region"],
            location_details["timezone"],
            location_details["latitude"],
            location_details["longitude"],
        )

        return location_details

    async def _async_get_list_data(self, url: str) -> list[Any]:
        """Retrieve data from AccuWeather API."""
        async with self._session.get(url, headers={"Content-Encoding": "gzip"}) as resp:
            if resp.status == HTTPStatus.UNAUTHORIZED.value:
                raise InvalidApiKeyError("Invalid API key")

            if resp.status != HTTPStatus.OK.value:
                try:
                    error_text = orjson.loads(await resp.text())
                except orjson.JSONDecodeError as exc:
                    raise ApiError(f"Can't decode API response: {exc}") from exc
                if (
                    error_text["Message"]
                    == "The allowed number of requests has been exceeded."
                ):
                    raise RequestsExceededError(
                        "The allowed number of requests has been exceeded"
                    )
                raise ApiError(f"Invalid response from AccuWeather API: {resp.status}")

            _LOGGER.debug("Data retrieved from %s, status: %s", url, resp.status)
            data = await resp.json()

        if resp.headers["RateLimit-Remaining"].isdigit():
            self._requests_remaining = int(resp.headers["RateLimit-Remaining"])

        if not isinstance(data, list):
            raise ApiError("Unexpected response from AccuWeather API: expected list")

        return data


def _parse_index_data(data: list[dict[str, Any]]) -> list[dict[str, dict[str, Any]]]:
    data.sort(key=lambda x: x["EpochDateTime"])

    grouped_data: dict[str, dict[str, Any]] = defaultdict(dict)
    for item in data:
        item.pop("ID")
        item.pop("Ascending")
        item.pop("Link")
        item.pop("MobileLink")

        name = item.pop("Name")
        date = item.pop("EpochDateTime")

        local = item.pop("LocalDateTime")
        local = local.split("T")[0]

        item["LocalDateTime"] = local

        grouped_data[date][name] = item

    return list(grouped_data.values())
