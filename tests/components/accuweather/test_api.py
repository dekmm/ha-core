"""Tests for the AccuWeatherExt."""

from unittest.mock import AsyncMock, MagicMock, patch

from aioresponses import aioresponses  # using to mock external HTTP requests
import pytest

from homeassistant.components.accuweather.api import AccuWeatherExt


@pytest.fixture
async def accuweather_mock():
    """AccuWeatherExt object will be mock along with mock data."""
    with patch.object(AccuWeatherExt, "__init__", lambda x: None):
        accuweather_mock = MagicMock(spec=AccuWeatherExt)
        accuweather_mock._location_key = "mock_location_key"
        accuweather_mock.api_key = "mock_api_key"
        return accuweather_mock


###Test for method :async_get_index_data###


@pytest.mark.asyncio
async def test_async_get_index_data(accuweather_mock):
    """1.Test to get the index data."""
    with aioresponses() as mock:
        url = (
            "https://dataservice.accuweather.com/indices/v1/daily/1day/mock_location_key/"
            "mock_index?apikey=mock_api_key&details=true"
        )
        mock_actual_response = [
            {
                "EpochDateTime": 1698450000,
                "Name": "Arthritis Pain Forecast",
                "Value": {"Value": 50},
                "ID": 21,
                "Ascending": True,
                "Link": "https://link.com",
                "MobileLink": "https://mobile_link.com",
            }
        ]
        mock.get(url, payload=mock_actual_response)
        ##Mock the method from api.py file##
        AccuWeatherExt.async_get_index_data = AsyncMock(
            return_value=[{1698450000: {"Arthritis Pain Forecast": {"Value": 50}}}]
        )
        output = await AccuWeatherExt.async_get_index_data(
            index_id="Arthritis Pain Forecast"
        )  # Method is being called to test
        assert output == [{1698450000: {"Arthritis Pain Forecast": {"Value": 50}}}]


@pytest.mark.asyncio
async def test_async_get_index_data_error(accuweather_mock):
    """2.Test for getting unauthorize errors."""
    with aioresponses() as mock:
        url = (
            "https://dataservice.accuweather.com/indices/v1/daily/1day/mock_location_key/"
            "mock_index?apikey=mock_api_key&details=true"
        )
        mock.get(url, status=401)

        AccuWeatherExt.async_get_index_data = AsyncMock(return_value=[])
        output = await AccuWeatherExt.async_get_index_data(
            index_id="Arthritis Pain Forecast"
        )
        assert output == []


@pytest.mark.asyncio
async def test_async_get_index_data_exceeded(accuweather_mock):
    """3.Test for exceeding rate limits."""
    with aioresponses() as mock:
        url = (
            "https://dataservice.accuweather.com/indices/v1/daily/1day/mock_location_key/"
            "mock_index?apikey=mock_api_key&details=true"
        )
        mock.get(url, status=429)

        AccuWeatherExt.async_get_index_data = AsyncMock(return_value=[])
        output = await AccuWeatherExt.async_get_index_data(
            index_id="Arthritis Pain Forecast"
        )
        assert output == []


@pytest.mark.asyncio
async def test_async_get_index_data_empty(accuweather_mock):
    """4.Test to handle empty API response."""
    with aioresponses() as mock:
        url = (
            "https://dataservice.accuweather.com/indices/v1/daily/1day/mock_location_key/"
            "mock_index?apikey=mock_api_key&details=true"
        )
        mock.get(url, payload=[])
        AccuWeatherExt.async_get_index_data = AsyncMock(return_value=[])
        output = await AccuWeatherExt.async_get_index_data(
            index_id="Arthritis Pain Forecast"
        )
        assert output == [], f"Empty Data Error {output}"


def test_parse_index_data(accuweather_mock):
    """5.Test for parsing of index data."""
    index_data = [
        {
            "EpochDateTime": 1698450000,
            "Name": "Arthritis Pain Forecast",
            "Value": {"Value": 50},
            "ID": 21,
            "Ascending": True,
            "LocalDateTime": "2023-11-12T12:00:00Z",
            "Link": "https://link.com",
            "MobileLink": "https://mobile_link.com",
        }
    ]
    expected_data = [{1698450000: {"Arthritis Pain Forecast": {"Value": 50}}}]
    AccuWeatherExt._parse_index_data = MagicMock(return_value=expected_data)
    output = AccuWeatherExt._parse_index_data(index_data)
    output = AccuWeatherExt._parse_index_data(index_data)
    assert output == expected_data
