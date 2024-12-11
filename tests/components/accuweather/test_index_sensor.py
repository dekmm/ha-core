"""Tests to validate the behavior of AccuWeather sensors."""

import pytest
from homeassistant.components.accuweather.sensor import INDEX_SENSOR_TYPES

# Mock Data for valid data
Mock_Sensor_Valid_Outputs = {
    "Healthy Heart Fitness Forecast": {
        "Value": 5.8,
        "Category": "Good",
        "CategoryValue": 2,
        "Text": "Good for fitness",
        "LocalDateTime": "2024-12-12T08:00:00",
    },
    "Dust & Dander Forecast": {
        "Value": 7.0,
        "Category": "High",
        "CategoryValue": 3,
        "Text": "Take precautions",
        "LocalDateTime": "2024-12-12T08:00:00",
    },
}

# Mock Data for invalid/empty data
Mock_Sensor_Invalid_Outputs = {
    "Healthy Heart Fitness Forecast": {},
    "Dust & Dander Forecast": {},
    "Arthritis Pain Forecast": {},
    "Asthma Forecast": {},
    "Common Cold Forecast": {},
    "Flu Forecast": {},
    "Migraine Headache Forecast": {},
}

# Expected options for each sensor
Expected_Options = {
    "Healthy Heart Fitness Forecast": [
        "Excellent",
        "Very Good",
        "Good",
        "Fair",
        "Poor",
    ],
    "Dust & Dander Forecast": ["Extreme", "Very High", "High", "Moderate", "Low"],
    "Arthritis Pain Forecast": [
        "At Extreme Risk",
        "At High Risk",
        "At Risk",
        "Neutral",
        "Beneficial",
    ],
    "Asthma Forecast": [
        "At Extreme Risk",
        "At High Risk",
        "At Risk",
        "Neutral",
        "Beneficial",
    ],
    "Common Cold Forecast": [
        "At Extreme Risk",
        "At High Risk",
        "At Risk",
        "Neutral",
        "Beneficial",
    ],
    "Flu Forecast": [
        "At Extreme Risk",
        "At High Risk",
        "At Risk",
        "Neutral",
        "Beneficial",
    ],
    "Migraine Headache Forecast": [
        "At Extreme Risk",
        "At High Risk",
        "At Risk",
        "Neutral",
        "Beneficial",
    ],
}


@pytest.mark.parametrize("sensor_description", INDEX_SENSOR_TYPES)
def test_sensor_valid_outputs(sensor_description):
    """Test that each sensor returns valid values."""
    mock_data = Mock_Sensor_Valid_Outputs.get(sensor_description.key, {})
    if mock_data:
        sensor_value = sensor_description.value_fn(mock_data)
        assert sensor_value is not None, (
            f"Sensor '{sensor_description.key}' returned None, "
            "indicating an issue with value extraction."
        )
    else:
        pytest.skip(f"No mock data available for sensor: {sensor_description.key}")


@pytest.mark.parametrize("sensor_description", INDEX_SENSOR_TYPES)
def test_sensor_invalid_outputs(sensor_description):
    """Test that sensors handle missing data gracefully."""
    mock_data = Mock_Sensor_Invalid_Outputs.get(sensor_description.key, {})
    if not mock_data:
        with pytest.raises(KeyError, match="Category"):
            sensor_description.value_fn(mock_data)
    else:
        pytest.skip(
            f"Unexpected mock data present for sensor: {sensor_description.key}"
        )


@pytest.mark.parametrize("sensor_description", INDEX_SENSOR_TYPES)
def test_sensor_options_are_correct(sensor_description):
    """Test that the defined options match the expected set of values."""
    if sensor_description.key in Expected_Options:
        assert (
            sensor_description.options == Expected_Options[sensor_description.key]
        ), f"Options for sensor '{sensor_description.key}' do not match the expected values."
    else:
        pytest.skip(f"No expected options defined for sensor: {sensor_description.key}")
