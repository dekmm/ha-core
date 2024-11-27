"""'Tests to validate the behavior of sensors."""

import pytest

from homeassistant.components.accuweather.sensor import INDEX_SENSOR_TYPES

# Mock Data for valid data
Mock_Sensor_Valid_Outputs = {
    "Healthy Heart Fitness Forecast": {"Category": "Good"},
    "Dust & Dander Forecast": {"Category": "High"},
    "Arthritis Pain Forecast": {"Category": "Neutral"},
    "Asthma Forecast": {"Category": "At Risk"},
    "Common Cold Forecast": {"Category": "Beneficial"},
    "Flu Forecast": {"Category": "At High Risk"},
    "Migraine Headache Forecast": {"Category": "At Extreme Risk"},
}

# Mock Data for empty data
Mock_Sensor_Invalid_Outputs = {
    "Healthy Heart Fitness Forecast": {},
    "Dust & Dander Forecast": {},
    "Arthritis Pain Forecast": {},
    "Asthma Forecast": {},
    "Common Cold Forecast": {},
    "Flu Forecast": {},
    "Migraine Headache Forecast": {},
}


@pytest.mark.parametrize("sensor_description", INDEX_SENSOR_TYPES)
def test_sensor_valid_outputs(sensor_description):
    """1.Test each sensor return valid values."""
    mock_data = Mock_Sensor_Valid_Outputs.get(sensor_description.key, {})
    sensor_value = sensor_description.value_fn(mock_data)
    assert sensor_value in sensor_description.options, (
        f"Sensor '{sensor_description.key}' returned value '{sensor_value}' "
        f"Error,It is not the valid sensor: {sensor_description.options}"
    )


@pytest.mark.parametrize("sensor_description", INDEX_SENSOR_TYPES)
def test_sensor_invalid_outputs(sensor_description):
    """2.Test sensor can handles missing data."""
    mock_data = Mock_Sensor_Invalid_Outputs.get(sensor_description.key, {})

    with pytest.raises(KeyError, match="Category"):  # will handle the exception check
        sensor_description.value_fn(mock_data)


@pytest.mark.parametrize("sensor_description", INDEX_SENSOR_TYPES)
def test_sensor_options_are_correct(sensor_description):
    """3.Test that the index match the expected set of values."""
    expected_options = {
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

    # Assert that actual and expected options in a sensor matches
    assert (
        sensor_description.options == expected_options[sensor_description.key]
    ), f"Options for sensors  '{sensor_description.key}' does not match with the valid values."

    ###Uncomment this to verify the failed tests###


# @pytest.mark.parametrize("sensor_description", INDEX_SENSOR_TYPES)
# def test_sensor_options_are_Not_correct(sensor_description):
# """Test that the defined index match the expected set of values."""

# expected_options = {
# "Healthy Heart Fitness Forecast": [
# "Excellent",
# "Very Good",
# "Good",
# "Fair",
# "Poor",
# ],
# "Dust & Dander Forecast": ["Extreme", "Very High", "High", "Moderate", "Low"],
# }
# Intentionally mismatch the expected output to test the code
# expected_options["Healthy Heart Fitness Forecast"] = ["Invalid", "Bad Data"]

# assert (
# sensor_description.options == expected_options[sensor_description.key]
# ), f"Options for sensors '{sensor_description.key}' does not match."
