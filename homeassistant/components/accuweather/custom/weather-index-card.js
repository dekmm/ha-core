class WeatherIndexCard extends HTMLElement {
  constructor() {
    super();
    this.charts = new Map(); // To track chart instances
  }

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
      // Add other sensor groups here
    };

    const allGroups = Object.entries(groupedSensors).map(([groupName, sensors]) => {
      const indices = sensors.map((sensor, i) => {
        const state = hass.states[sensor];
        const stateStr = state ? state.state : "unavailable";
        const icon = state ? state.attributes.icon : "mdi:weather-cloudy";
        return {
          name: `Day ${i + 1}`,
          value: stateStr,
          numericValue: enumMapping[stateStr] || 0,
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
        .group {
          margin-bottom: 30px;
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
      <div class="weather-index-card">
        ${allGroups
          .map(
            (group) => `
          <div class="group">
            <h3>${group.groupName}</h3>
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
        const canvasId = `graph-${group.groupName.replace(/\s+/g, "-")}`;
        const ctx = this.querySelector(`#${canvasId}`);
        this.renderGraph(ctx, group.indices, reverseMapping, canvasId);
      });
    }, 1000);
  }

  renderGraph(ctx, indices, reverseMapping, canvasId) {
    // Destroy existing chart if it exists
    if (this.charts.has(canvasId)) {
      this.charts.get(canvasId).destroy();
      this.charts.delete(canvasId); // Remove from map after destruction
    }

    const data = indices.map((index) => index.numericValue);
    const labels = indices.map((index) => index.name);

    const chart = new Chart(ctx, {
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

    // Save the chart instance to the map
    this.charts.set(canvasId, chart);
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
