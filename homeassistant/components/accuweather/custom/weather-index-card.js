import "https://cdn.jsdelivr.net/npm/chart.js";

console.log("Weather Index Card Loaded!");

class WeatherIndexCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      this.render(hass);
    }
  }

  render(hass) {
    const locationCityState =
      hass.states["sensor.home_location_city"];
    const locationCountryState =
      hass.states["sensor.home_location_country"];

    const locationCity = locationCityState
      ? locationCityState.state
      : "City Unavailable";
    const locationCountry = locationCountryState
      ? locationCountryState.state
      : "Country Unavailable";

    const COLORS = {
      gradients: {
        severity5:
          "linear-gradient(135deg, rgba(255, 0, 0, 0.9), rgba(255, 87, 51, 0.8))", // Red-Orange
        severity4:
          "linear-gradient(135deg, rgba(255, 87, 51, 0.9), rgba(255, 165, 0, 0.8))", // Orange
        severity3:
          "linear-gradient(135deg, rgba(255, 165, 0, 0.9), rgba(255, 255, 0, 0.8))", // Yellow
        severity2:
          "linear-gradient(135deg, rgba(255, 255, 0, 0.9), rgba(0, 128, 0, 0.8))", // Yellow-Green
        severity1:
          "linear-gradient(135deg, rgba(0, 128, 0, 0.9), rgba(0, 255, 128, 0.8))", // Green
        default:
          "linear-gradient(135deg, rgba(128, 128, 128, 0.9), rgba(200, 200, 200, 0.8))", // Gray
      },
      plotColors: {
        migraine: {
          borderColor: "rgba(255, 99, 132, 1)", // Red
          backgroundColor: "rgba(255, 99, 132, 0.1)", // Light Red
        },
        asthma: {
          borderColor: "rgba(54, 162, 235, 1)", // Blue
          backgroundColor: "rgba(54, 162, 235, 0.1)", // Light Blue
        },
        arthritis: {
          borderColor: "rgba(75, 192, 192, 1)", // Teal
          backgroundColor: "rgba(75, 192, 192, 0.1)", // Light Teal
        },
        commonCold: {
          borderColor: "rgba(255, 206, 86, 1)", // Yellow
          backgroundColor: "rgba(255, 206, 86, 0.1)", // Light Yellow
        },
        flu: {
          borderColor: "rgba(153, 102, 255, 1)", // Purple
          backgroundColor: "rgba(153, 102, 255, 0.1)", // Light Purple
        },
        healthyHeart: {
          borderColor: "rgba(0, 123, 255, 1)", // Blue
          backgroundColor: "rgba(0, 123, 255, 0.1)", // Light Blue
        },
        dustDander: {
          borderColor: "rgba(124, 252, 0, 1)", // Green
          backgroundColor: "rgba(124, 252, 0, 0.1)", // Light Green
        },
      },
    };

    const today = new Date();
    const formattedDate = today.toLocaleDateString("en-US", {
      weekday: "long",
      month: "long",
      day: "numeric",
      year: "numeric",
    });

    const enumMapping = {
      // All
      "At Extreme Risk": 5,
      "At High Risk": 4,
      "At Risk": 3,
      Neutral: 2,
      Beneficial: 1,
      unavailable: 0,
      Unavailable: 0,

      // Healthy Heart Fitness Forecast
      Excellent: 1,
      "Very Good": 2,
      Good: 3,
      Fair: 4,
      Poor: 5,

      // Dust and Dander Forecast
      Extreme: 5,
      "Very High": 4,
      High: 3,
      Moderate: 2,
      Low: 1,
    };

    const reverseMapping = {
      5: "At Extreme Risk",
      4: "At High Risk",
      3: "At Risk",
      2: "Neutral",
      1: "Beneficial",
      0: "unavailable",

      // Healthy Heart Fitness Forecast
      1: "Excellent",
      2: "Very Good",
      3: "Good",
      4: "Fair",
      5: "Poor",

      // Dust and Dander Forecast
      5: "Extreme",
      4: "Very High",
      3: "High",
      2: "Moderate",
      1: "Low",
    };

    const getColorBySeverity = (severity) => {
      switch (severity) {
        case 5:
          return COLORS.gradients.severity5;
        case 4:
          return COLORS.gradients.severity4;
        case 3:
          return COLORS.gradients.severity3;
        case 2:
          return COLORS.gradients.severity2;
        case 1:
          return COLORS.gradients.severity1;
        default:
          return COLORS.gradients.default;
      }
    };

    const datasetColorMapping = {
      "Migraine Risk": COLORS.plotColors.migraine,
      "Asthma Risk": COLORS.plotColors.asthma,
      "Arthritis Pain": COLORS.plotColors.arthritis,
      "Common Cold": COLORS.plotColors.commonCold,
      Flu: COLORS.plotColors.flu,
      "Healthy Heart Fitness": COLORS.plotColors.healthyHeart,
      "Dust & Dander": COLORS.plotColors.dustDander,
      default: COLORS.plotColors.default,
    };

    const todaySensors = [
      {
        sensor: "sensor.home_arthritis_pain_forecast",
        icon: "mdi:human-walker",
        name: "Arthritis Pain",
      },
      {
        sensor: "sensor.home_asthma_forecast",
        icon: "mdi:lungs",
        name: "Asthma",
      },
      {
        sensor: "sensor.home_common_cold_forecast",
        icon: "mdi:snowflake-thermometer",
        name: "Common Cold",
      },
      {
        sensor: "sensor.home_flu_forecast",
        icon: "mdi:emoticon-sick",
        name: "Flu",
      },
      {
        sensor: "sensor.home_migraine_headache_forecast",
        icon: "mdi:head-flash",
        name: "Migraine Headache",
      },
      {
        sensor: "sensor.home_healthy_heart_fitness_forecast",
        icon: "mdi:heart-pulse",
        name: "Healthy Heart Fitness",
      },
      {
        sensor: "sensor.home_dust_dander_forecast",
        icon: "mdi:air-filter",
        name: "Dust & Dander",
      },
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
      "Healthy Heart Fitness Forecast": [
        "sensor.home_healthy_heart_fitness_forecast",
        "sensor.home_healthy_heart_fitness_forecast_2",
        "sensor.home_healthy_heart_fitness_forecast_3",
        "sensor.home_healthy_heart_fitness_forecast_4",
        "sensor.home_healthy_heart_fitness_forecast_5",
      ],
      "Dust and Dander Forecast": [
        "sensor.home_dust_dander_forecast",
        "sensor.home_dust_dander_forecast_2",
        "sensor.home_dust_dander_forecast_3",
        "sensor.home_dust_dander_forecast_4",
        "sensor.home_dust_dander_forecast_5",
      ],
    };

    const todayIndices = todaySensors.map(({ sensor, icon, name }) => {
      const state = hass.states[sensor];
      const stateStr = state ? state.state : "unavailable";
      const numericValue = enumMapping[stateStr] || 0;
      const borderColor =
        datasetColorMapping[name] || datasetColorMapping.default; // Default to gray if no match
      return {
        name: name,
        value: stateStr,
        numericValue: numericValue,
        icon: icon || "mdi:weather-cloudy",
        color: getColorBySeverity(numericValue),
        borderColor: borderColor, // Use dataset color
      };
    });

    // Retrieve data dynamically for the chart
    const forecastData = Object.entries(groupedSensors).reduce(
      (acc, [key, sensors]) => {
        acc[key] = sensors.map((sensor) => {
          const state = hass.states[sensor];
          const stateStr = state ? state.state : "unavailable";
          return enumMapping[stateStr] || 0;
        });
        return acc;
      },
      {},
    );

    const generateDateLabels = (numDays) => {
      const today = new Date();
      const labels = [];
      for (let i = 0; i < numDays; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() + i);
        labels.push(
          date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
        );
      }
      return labels;
    };

    const date_labels = generateDateLabels(5);

    this.innerHTML = `
      <style>
    .location-date-card {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 20px;
          margin-bottom: 20px;
          border-radius: 15px;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
          background: linear-gradient(135deg, rgba(135, 206, 235, 0.9), rgba(255, 182, 193, 0.8));
          font-size: 18px;
          font-weight: bold;
          color: white;
          text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
          animation: fadeIn 1s ease-in-out;
        }

        .location {
          font-size: 20px;
          margin-bottom: 8px;
        }

        .date {
          font-size: 16px;
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

  .weather-index-card {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 8px; /* Reduced space between cards */
    margin-bottom: 16px; /* Adjusted bottom margin */
  }

  .today-icon-box {
    padding: 10px; /* Reduced padding for smaller cards */
    text-align: center;
    border-radius: 20px; /* Slightly smaller border radius */
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.2); /* Adjusted shadow */
    color: white;
    background: var(--icon-color, rgba(0, 0, 0, 0.7));
    transition: box-shadow 0.2s ease-in-out, transform 0.2s ease-in-out;
  }

  .today-icon-box:hover {
    transform: scale(1.03); /* Slight hover effect */
    box-shadow: 0 5px 10px rgba(0, 0, 0, 0.3); /* Slightly smaller hover shadow */
  }

  .icon {
    margin: 0 auto;
    font-size: 32px; /* Reduced icon size */
    width: 40px; /* Reduced icon container width */
    height: 40px; /* Reduced icon container height */
    background: rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .today-name {
    font-size: 12px; /* Smaller text size for name */
    font-weight: bold;
    margin-top: 6px;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
  }

  .today-label {
    font-size: 10px; /* Smaller text size for label */
    font-weight: 300;
    margin-top: 2px;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
  }

        .forecast-chart {
          width: 100%;
          height: 300px;
          margin-top: 20px;
        }
      </style>
      <div class="location-date-card">
        <div class="location">${locationCity}, ${locationCountry}</div>
        <div class="date">${formattedDate}</div>
      </div>
      <div class="weather-index-card">
        ${todayIndices
          .map(
            (index) => `
            <div class="today-icon-box"
     style="background: ${index.color}; --icon-color: ${index.color}; border: 12px solid ${index.borderColor};">
  <div class="icon">

              <ha-icon icon="${index.icon}"></ha-icon>
            </div>
            <div class="today-name">${index.name}</div>
            <div class="today-label">${index.value}</div>
          </div>
        `,
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
          labels: date_labels,
          datasets: [
            {
              label: "Migraine Risk",
              data: forecastData["Migraine Headache Forecast"],
              borderColor: COLORS.plotColors.migraine.borderColor,
              backgroundColor: COLORS.plotColors.migraine.backgroundColor,
              fill: true,
              tension: 0.4,
            },
            {
              label: "Asthma Risk",
              data: forecastData["Asthma Forecast"],
              borderColor: COLORS.plotColors.asthma.borderColor,
              backgroundColor: COLORS.plotColors.asthma.backgroundColor,
              fill: true,
              tension: 0.4,
            },
            {
              label: "Arthritis Pain",
              data: forecastData["Arthritis Pain Forecast"],
              borderColor: COLORS.plotColors.arthritis.borderColor,
              backgroundColor: COLORS.plotColors.arthritis.backgroundColor,
              fill: true,
              tension: 0.4,
            },
            {
              label: "Common Cold",
              data: forecastData["Common Cold Forecast"],
              borderColor: COLORS.plotColors.commonCold.borderColor,
              backgroundColor: COLORS.plotColors.commonCold.backgroundColor,
              fill: true,
              tension: 0.4,
            },
            {
              label: "Flu",
              data: forecastData["Flu Forecast"],
              borderColor: COLORS.plotColors.flu.borderColor,
              backgroundColor: COLORS.plotColors.flu.backgroundColor,
              fill: true,
              tension: 0.4,
            },
            {
              label: "Healthy Heart Fitness",
              data: forecastData["Healthy Heart Fitness Forecast"],
              borderColor: COLORS.plotColors.healthyHeart.borderColor,
              backgroundColor: COLORS.plotColors.healthyHeart.backgroundColor,
              fill: true,
              tension: 0.4,
            },
            {
              label: "Dust & Dander",
              data: forecastData["Dust and Dander Forecast"],
              borderColor: COLORS.plotColors.dustDander.borderColor,
              backgroundColor: COLORS.plotColors.dustDander.backgroundColor,
              fill: true,
              tension: 0.4,
            },
          ],
        },
        options: {
          plugins: {
            legend: {
              labels: {
                usePointStyle: true,
                pointStyle: "circle",
                position: "bottom",
                color: "white", // Label color
                font: {
                  size: 14, // Font size
                  weight: "bold", // Font weight
                },
              },
            },
          },
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
              max: 5,
              title: {
                display: true,
                text: "Risk Level",
              },
              ticks: {
                stepSize: 1,
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
