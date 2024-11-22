import "https://cdn.jsdelivr.net/npm/chart.js";

class WeatherIndexCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      this.render(hass);
    }
  }

  render(hass) {
    const sensors = [
      "sensor.home_none_1",
      "sensor.home_none_2",
      "sensor.home_none_3",
      "sensor.home_none_4",
      "sensor.home_none_5",
    ];

    const enumMapping = {
      Low: 1,
      Moderate: 2,
      High: 3,
      "Very High": 4,
      Extreme: 5,
      unavailable: 0,
    };

    const indices = [
      {
        name: "sensor.home_none_1",
        value: "Low",
        numericValue: enumMapping["Low"] || 0,
        icon: "mdi:weather-cloudy",
      },
      {
        name: "sensor.home_none_2",
        value: "Moderate",
        numericValue: enumMapping["Moderate"] || 0,
        icon: "mdi:weather-cloudy",
      },
      {
        name: "sensor.home_none_5",
        value: "Extreme",
        numericValue: enumMapping["Extreme"] || 0,
        icon: "mdi:weather-cloudy",
      },
      {
        name: "sensor.home_none_3",
        value: "High",
        numericValue: enumMapping["High"] || 0,
        icon: "mdi:weather-cloudy",
      },
      {
        name: "sensor.home_none_4",
        value: "Very High",
        numericValue: enumMapping["Very High"] || 0,
        icon: "mdi:weather-cloudy",
      },
    ];

    // const indices = sensors.map(sensor => {
    //   // const state = hass.states[sensor];
    //   // const stateStr = state ? state.state : "unavailable";
    //   // const icon = state ? state.attributes.icon : "mdi:weather-cloudy";
    //   return {
    //     name: sensor,
    //     value: stateStr,
    //     numericValue: enumMapping[stateStr] || 0, // Map enum to numeric
    //     icon: icon
    //   };
    // });

    this.innerHTML = `
      <style>
        .weather-index-card {
          display: flex;
          flex-direction: column;
          gap: 20px;
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
        .graph-container {
          position: relative;
          width: 100%;
          height: 150px;
        }
      </style>
      <div class="weather-index-card">
        <div class="boxes">
          ${indices
            .map(
              (index) => `
            <div class="box">
              <ha-icon class="icon" icon="${index.icon}"></ha-icon>
              <div>${index.value}</div>
            </div>
          `,
            )
            .join("")}
        </div>
        <div class="graph-container">
          <canvas id="weather-graph"></canvas>
        </div>
      </div>
    `;

    let rd = setInterval(() => {
      if (this.querySelector("#weather-graph")) {
        clearInterval(rd);
        this.renderGraph(indices);
      }
    }, 1000);
  }

  renderGraph(indices) {
    const ctx = this.querySelector("#weather-graph");
    const data = indices.map((index) => index.numericValue);
    const labels = indices.map((_, i) => `Day ${i + 1}`);

    new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Index Value",
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
            min: 1,
            max: 5,
            title: {
              display: true,
              text: "Index Value",
            },
            ticks: {
              callback: function (value) {
                const reverseMapping = {
                  1: "Low",
                  2: "Moderate",
                  3: "High",
                  4: "Very High",
                  5: "Extreme",
                  0: "unavailable",
                };
                return reverseMapping[value];
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
