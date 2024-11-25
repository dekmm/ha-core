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

    const getColorBySeverity = (severity) => {
      switch (severity) {
        case 6:
          return "linear-gradient(135deg, rgba(255, 0, 0, 0.9), rgba(255, 87, 51, 0.8))";
        case 5:
          return "linear-gradient(135deg, rgba(255, 87, 51, 0.9), rgba(255, 165, 0, 0.8))";
        case 4:
          return "linear-gradient(135deg, rgba(255, 165, 0, 0.9), rgba(255, 255, 0, 0.8))";
        case 3:
          return "linear-gradient(135deg, rgba(255, 255, 0, 0.9), rgba(0, 128, 0, 0.8))";
        case 2:
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
    `;
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
