import "https://cdn.jsdelivr.net/npm/chart.js";

console.log('Weather Index Card Loaded!');

class WeatherIndexCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      this.render(hass);
    }
  }

  render(hass) {
    const enumMapping = {
      "At Extreme Risk": 5,
      "At High Risk": 4,
      "At Risk": 3,
      Neutral: 2,
      Beneficial: 1,
      unavailable: 0,
    };

    const reverseMapping = {
      5: "At Extreme Risk",
      4: "At High Risk",
      3: "At Risk",
      2: "Neutral",
      1: "Beneficial",
      0: "unavailable",
    };

    const getColorBySeverity = (severity) => {
      switch (severity) {
        case 5:
          return "linear-gradient(135deg, rgba(255, 0, 0, 0.9), rgba(255, 87, 51, 0.8))";
        case 4:
          return "linear-gradient(135deg, rgba(255, 87, 51, 0.9), rgba(255, 165, 0, 0.8))";
        case 3:
          return "linear-gradient(135deg, rgba(255, 165, 0, 0.9), rgba(255, 255, 0, 0.8))";
        case 2:
          return "linear-gradient(135deg, rgba(255, 255, 0, 0.9), rgba(0, 128, 0, 0.8))";
        case 1:
          return "linear-gradient(135deg, rgba(0, 128, 0, 0.9), rgba(0, 255, 128, 0.8))";
        default:
          return "linear-gradient(135deg, rgba(128, 128, 128, 0.9), rgba(200, 200, 200, 0.8))";
      }
    };

    const todaySensors = [
      { sensor: "sensor.home_arthritis_pain_forecast", icon: "mdi:human-walker", name: "Arthritis Pain" },
      { sensor: "sensor.home_asthma_forecast", icon: "mdi:lungs", name: "Asthma" },
      { sensor: "sensor.home_common_cold_forecast", icon: "mdi:snowflake-thermometer", name: "Common Cold" },
      { sensor: "sensor.home_flu_forecast", icon: "mdi:emoticon-sick", name: "Flu" },
      { sensor: "sensor.home_migraine_headache_forecast", icon: "mdi:head-flash", name: "Migraine Headache" },
    ];

    const groupedSensors = {
      "Arthritis Pain Forecast": [
        "sensor.home_arthritis_pain_forecast",
        "sensor.home_arthritis_pain_forecast_2",
        "sensor.home_arthritis_pain_forecast_3",
        "sensor.home_arthritis_pain_forecast_4",
        "sensor.home_arthritis_pain_forecast_5",
      ],
      "Asthma Forecast": [
        "sensor.home_asthma_forecast",
        "sensor.home_asthma_forecast_2",
        "sensor.home_asthma_forecast_3",
        "sensor.home_asthma_forecast_4",
        "sensor.home_asthma_forecast_5",
      ],
      "Common Cold Forecast": [
        "sensor.home_common_cold_forecast",
        "sensor.home_common_cold_forecast_2",
        "sensor.home_common_cold_forecast_3",
        "sensor.home_common_cold_forecast_4",
        "sensor.home_common_cold_forecast_5",
      ],
      "Flu Forecast": [
        "sensor.home_flu_forecast",
        "sensor.home_flu_forecast_2",
        "sensor.home_flu_forecast_3",
        "sensor.home_flu_forecast_4",
        "sensor.home_flu_forecast_5",
      ],
      "Migraine Headache Forecast": [
        "sensor.home_migraine_headache_forecast",
        "sensor.home_migraine_headache_forecast_2",
        "sensor.home_migraine_headache_forecast_3",
        "sensor.home_migraine_headache_forecast_4",
        "sensor.home_migraine_headache_forecast_5",
      ],
    };

    const todayIndices = todaySensors.map(({ sensor, icon, name }) => {
      const state = hass.states[sensor];
      const stateStr = state ? state.state : "unavailable";
      const numericValue = enumMapping[stateStr] || 0;
      return {
        name: name,
        value: stateStr,
        numericValue: numericValue,
        icon: icon || "mdi:weather-cloudy",
        color: getColorBySeverity(numericValue),
      };
    });

    // Retrieve data dynamically for the chart
    const forecastData = Object.entries(groupedSensors).reduce((acc, [key, sensors]) => {
      acc[key] = sensors.map((sensor) => {
        const state = hass.states[sensor];
        const stateStr = state ? state.state : "unavailable";
        return enumMapping[stateStr] || 0;
      });
      return acc;
    }, {});

    const labels = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"];

    this.innerHTML = `
      <style>
        .weather-index-card {
          display: grid;
          grid-template-columns: repeat(5, 1fr); /* Force 5 cards in a single row */
          gap: 10px; /* Space between cards */
          margin-bottom: 20px;
        }
        .today-icon-box {
          padding: 15px; /* Compact padding */
          text-align: center;
          border-radius: 12px;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
          color: white;
          background: var(--icon-color, rgba(0, 0, 0, 0.7));
          transition: box-shadow 0.2s ease-in-out, transform 0.2s ease-in-out;
        }
        .today-icon-box:hover {
          transform: scale(1.05); /* Slight hover effect */
          box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
        }
        .icon {
          margin: 0 auto;
          font-size: 40px; /* Adjusted icon size */
          width: 50px;
          height: 50px;
          background: rgba(255, 255, 255, 0.3);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .today-name {
          font-size: 14px; /* Compact text size */
          font-weight: bold;
          margin-top: 8px;
          text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        }
        .today-label {
          font-size: 12px; /* Smaller label size */
          font-weight: 300;
          margin-top: 4px;
          text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
        }
        .forecast-chart {
          width: 100%;
          height: 300px;
          margin-top: 20px;
        }
      </style>
      <div class="weather-index-card">
        ${todayIndices
          .map(
            (index) => `
          <div class="today-icon-box" style="background: ${index.color}; --icon-color: ${index.color}">
            <div class="icon">
              <ha-icon icon="${index.icon}"></ha-icon>
            </div>
            <div class="today-name">${index.name}</div>
            <div class="today-label">${index.value}</div>
          </div>
        `
          )
          .join("")}
      </div>
      <canvas id="forecastChart" class="forecast-chart"></canvas>
    `;

    // Render the chart after the DOM is updated
    setTimeout(() => {
      const ctx = this.querySelector("#forecastChart").getContext("2d");
      new Chart(ctx, {
        type: "line",
        data: {
          labels: labels,
          datasets: [
            {
              label: "Migraine Risk",
              data: forecastData["Migraine Headache Forecast"],
              borderColor: "rgba(255, 99, 132, 1)", // Red
              backgroundColor: "rgba(255, 99, 132, 0.2)", // Light red
              fill: true,
            },
            {
              label: "Asthma Risk",
              data: forecastData["Asthma Forecast"],
              borderColor: "rgba(54, 162, 235, 1)", // Blue
              backgroundColor: "rgba(54, 162, 235, 0.2)", // Light blue
              fill: true,
            },
            {
              label: "Arthritis Pain",
              data: forecastData["Arthritis Pain Forecast"],
              borderColor: "rgba(75, 192, 192, 1)", // Teal
              backgroundColor: "rgba(75, 192, 192, 0.2)", // Light teal
              fill: true,
            },
            {
              label: "Common Cold",
              data: forecastData["Common Cold Forecast"],
              borderColor: "rgba(255, 206, 86, 1)", // Yellow
              backgroundColor: "rgba(255, 206, 86, 0.2)", // Light yellow
              fill: true,
            },
            {
              label: "Flu",
              data: forecastData["Flu Forecast"],
              borderColor: "rgba(153, 102, 255, 1)", // Purple
              backgroundColor: "rgba(153, 102, 255, 0.2)", // Light purple
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              title: {
                display: true,
                text: "Days",
              },
            },
            y: {
              min: 0,
              max: 6,
              title: {
                display: true,
                text: "Risk Level",
              },
            },
          },
        },
      });
    }, 500);
  }

  setConfig(config) {
    if (!config) {
      throw new Error("Invalid configuration");
    }
  }

  static getConfigElement() {
    return document.createElement("hui-generic-entity-row");
  }

  getCardSize() {
    return 2;
  }
}

customElements.define("weather-index-card", WeatherIndexCard);
