"""Define tests for the AccuWeather config flow."""

from unittest.mock import AsyncMock, patch

from accuweather import ApiError, InvalidApiKeyError, RequestsExceededError
import pytest  # added

from homeassistant.components.accuweather.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant

# from homeassistant.data_entry_flow import FlowResultType
# from tests.common import MockConfigEntry

VALID_CONFIG = {
    CONF_NAME: "abcd",
    CONF_API_KEY: "32-character-string-1234567890qw",
    CONF_LATITUDE: 55.55,
    CONF_LONGITUDE: 122.12,
}


# modification
@pytest.fixture
def mock_accuweather_client():
    """Mock the AccuWeather client."""
    mock_client = AsyncMock()
    mock_client.async_get_location = AsyncMock()
    return mock_client


async def test_invalid_api_key(
    hass: HomeAssistant, mock_accuweather_client: AsyncMock
) -> None:
    """Test that errors are shown when API key is invalid."""
    # Modification-Simulate an InvalidApiKeyError
    mock_accuweather_client.async_get_location.side_effect = InvalidApiKeyError(
        "Invalid API key"
    )

    # modified 3 lines Correctly patch the AccuWeather class used in config_flow.py
    with patch(
        "homeassistant.components.accuweather.config_flow.AccuWeather",
        return_value=mock_accuweather_client,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}, data=VALID_CONFIG
        )

    assert result["errors"] == {CONF_API_KEY: "invalid_api_key"}


async def test_api_error(
    hass: HomeAssistant, mock_accuweather_client: AsyncMock
) -> None:
    """Test that API errors are handled."""
    mock_accuweather_client.async_get_location.side_effect = ApiError("API error")

    # modified 3 lines
    with patch(
        "homeassistant.components.accuweather.config_flow.AccuWeather",
        return_value=mock_accuweather_client,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}, data=VALID_CONFIG
        )

    assert result["errors"] == {"base": "cannot_connect"}


async def test_requests_exceeded_error(
    hass: HomeAssistant, mock_accuweather_client: AsyncMock
) -> None:
    """Test request exceeded error."""
    mock_accuweather_client.async_get_location.side_effect = RequestsExceededError(
        "The allowed number of requests has been exceeded"
    )
    # modified 3 lines
    with patch(
        "homeassistant.components.accuweather.config_flow.AccuWeather",
        return_value=mock_accuweather_client,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}, data=VALID_CONFIG
        )

    assert result["errors"] == {CONF_API_KEY: "requests_exceeded"}
