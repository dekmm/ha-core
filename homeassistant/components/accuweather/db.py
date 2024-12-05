"""AccuWeather index data store."""

import sqlite3
from typing import Any

from homeassistant.core import HomeAssistant


class AccuWeatherIndexGroupDataStore:
    """Class to handle the index data store."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the index data store."""
        self.hass = hass

    def _get_db_path(self) -> str:
        """Get the database path."""
        return self.hass.config.path("home-assistant_v2.db")

    async def async_create_index_data_table(self) -> None:
        """Asynchronously create the index data table if it doesn't exist."""

        def create_table() -> None:
            with sqlite3.connect(self._get_db_path()) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS accuweather_index_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        location_key TEXT NOT NULL,
                        index_group TEXT NOT NULL,
                        index_value INT NOT NULL,
                        category TEXT NOT NULL,
                        category_value INT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        UNIQUE (location_key, index_group, timestamp) ON CONFLICT IGNORE
                    )
                """)
                conn.commit()

        await self.hass.async_add_executor_job(create_table)

    async def async_insert_data(
        self,
        location_key: str,
        index_group: str,
        index_value: str,
        category: str,
        category_value: str,
        timestamp: str,
    ) -> None:
        """Asynchronously insert data into the index data table."""

        def insert_data() -> None:
            with sqlite3.connect(self._get_db_path()) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO accuweather_index_data (
                        location_key,
                        index_group,
                        index_value,
                        category,
                        category_value,
                        timestamp
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        location_key,
                        index_group,
                        index_value,
                        category,
                        category_value,
                        timestamp,
                    ),
                )
                conn.commit()

        await self.hass.async_add_executor_job(insert_data)

    async def async_query_data(
        self, location_key: str, index_group: str, timestamp: str
    ) -> Any:
        """Asynchronously query data by index group and timestamp."""

        def query_data() -> Any:
            with sqlite3.connect(self._get_db_path()) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT * FROM accuweather_index_data
                    WHERE location_key = ? AND index_group = ? AND timestamp = ?
                """,
                    (
                        location_key,
                        index_group,
                        timestamp,
                    ),
                )
                return cursor.fetchone()

        return await self.hass.async_add_executor_job(query_data)
