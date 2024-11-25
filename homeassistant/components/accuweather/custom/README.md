# Custom component for AccuWeather - Installation

1. Create a directory named `www` in your `config` directory.
2. Copy `weather-index-card.js` to `config/www` directory.
3. Go to `http://localhost:8123/profile/general` and enable Advanced mode.
4. Go to `http://localhost:8123/config/lovelace/resources` and add a resource with the following URL: `http://localhost:8123/local/weather-index-card.js` and Resource type: `JavaScript Module`.
5. Click on the Add Card button in the dashboard editor and select the Manual card at the bottom.
6. Paste the following configuration into the card editor and save it.

```yaml
type: 'custom:weather-index-card'
```