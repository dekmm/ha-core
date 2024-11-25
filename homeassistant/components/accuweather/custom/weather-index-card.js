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
      "At Extreme Risk": 6,
      "At High Risk": 5,
      "At Risk": 4,
      Neutral: 3,
      Beneficial: 2,
      unavailable: 0,
    };

    const reverseMapping = {
      6: "At Extreme Risk",
      5: "At High Risk",
      4: "At Risk",
      3: "Neutral",
      2: "Beneficial",
      0: "unavailable",
    };

    const todaySensors = [
      {
        sensor: "sensor.home_arthritis_pain_forecast",
        icon: "mdi:human-walker",
        name: "Arthritis Pain Forecast",
        color: "#FF5733" // Red-Orange
      },
      {
        sensor: "sensor.home_asthma_forecast",
        icon: "mdi:lungs",
        name: "Asthma Forecast",
        color: "#33A1FF" // Blue
      },
      {
        sensor: "sensor.home_common_cold_forecast",
        icon: "mdi:snowflake-thermometer",
        name: "Common Cold Forecast",
        color: "#76FF33" // Green
      },
      {
        sensor: "sensor.home_flu_forecast",
        icon: "mdi:emoticon-sick",
        name: "Flu Forecast",
        color: "#FFC300" // Yellow
      },
      {
        sensor: "sensor.home_migraine_headache_forecast",
        icon: "mdi:head-flash",
        name: "Migraine Headache Forecast",
        color: "#C70039" // Deep Red
      },
    ];
    const todayIndices = todaySensors.map(({ sensor, icon }) => {
      const state = hass.states[sensor];
      const stateStr = state ? state.state : "unavailable";
      return {
        name: sensor,
        value: stateStr,
        numericValue: enumMapping[stateStr] || 0, // Map enum to numeric
        icon: icon || "mdi:weather-cloudy",
      };
    });

    // Grouped sensors for 5-day forecasts
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

    const allGroups = Object.entries(groupedSensors).map(([groupName, sensors]) => {
      const indices = sensors.map((sensor, i) => {
        const state = hass.states[sensor];
        const stateStr = state ? state.state : "unavailable";
        const icon = state ? state.attributes.icon : "mdi:weather-cloudy";
        return {
          name: `Day ${i + 1}`,
          value: stateStr,
          numericValue: enumMapping[stateStr] || 0, // Map enum to numeric
          icon: icon,
        };
      });
      return { groupName, indices };
    });

    this.innerHTML = `
      <style>
        .weather-index-card {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }
        .today-icons {
          display: flex;
          justify-content: space-around;
          margin-bottom: 20px;
        }
        .today-icon-box {
          background: #1c1c1c;
          padding: 10px;
          text-align: center;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          flex: 1;
          margin: 0 5px;
        }
        .group {
          margin-bottom: 30px;
        }
        .boxes {
          display: grid;
          grid-template-columns: repeat(5, 1fr);
          gap: 10px;
        }
        .box {
          background: #1c1c1c;
          padding: 15px;
          text-align: center;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .icon {
          font-size: 24px;
          margin-bottom: 5px;
        }
        .today-label {
          font-size: 14px;
        }
        .graph-container {
          position: relative;
          width: 100%;
          height: 150px;
        }
        h3 {
          margin-bottom: 10px;
        }
      </style>
      <div class="today-icons">
        ${todayIndices
          .map(
            (index) => `
          <div class="today-icon-box">
            <ha-icon class="icon" icon="${index.icon}"></ha-icon>
            <div class="today-label">${index.value}</div>
            <div class="today-name">${index.name}</div>
          </div>
        `,
          )
          .join("")}
      </div>
      <div class="weather-index-card">
        ${allGroups
          .map(
            (group) => `
          <div class="group">
            <h3>${group.groupName}</h3>
            <div class="boxes">
              ${group.indices
                .map(
                  (index) => `
                <div class="box">
                  <ha-icon class="icon" icon="${index.icon}"></ha-icon>
                  <div>${index.name}: ${index.value}</div>
                </div>
              `,
                )
                .join("")}
            </div>
            <div class="graph-container">
              <canvas id="graph-${group.groupName.replace(/\s+/g, "-")}"></canvas>
            </div>
          </div>
        `,
          )
          .join("")}
      </div>
    `;

    // Render graphs for each group
    setTimeout(() => {
      allGroups.forEach((group) => {
        const ctx = this.querySelector(
          `#graph-${group.groupName.replace(/\s+/g, "-")}`,
        );
        this.renderGraph(ctx, group.indices, reverseMapping);
      });
    }, 1000);
  }

  renderGraph(ctx, indices, reverseMapping) {
    const data = indices.map((index) => index.numericValue);
    const labels = indices.map((index) => index.name);

    new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Severity Level",
            data: data,
            borderColor: "rgba(75, 192, 192, 1)",
            backgroundColor: "rgba(75, 192, 192, 0.2)",
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
              text: "Day",
            },
          },
          y: {
            min: 0,
            max: 6,
            title: {
              display: true,
              text: "Severity Level",
            },
            ticks: {
              callback: function (value) {
                return reverseMapping[value] || "unknown";
              },
            },
          },
        },
      },
    });
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
