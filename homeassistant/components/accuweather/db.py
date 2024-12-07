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
                        text TEXT NOT NULL,
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
        text: str,
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
                        timestamp,
                        text
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        location_key,
                        index_group,
                        index_value,
                        category,
                        category_value,
                        timestamp,
                        text,
                    ),
                )
                conn.commit()

        await self.hass.async_add_executor_job(insert_data)

    async def async_query_data(
        self, location_key: str, timestamp: str
    ) -> dict[str, dict]:
        """Asynchronously query data by index group and timestamp."""

        def query_data() -> dict[str, dict]:
            with sqlite3.connect(self._get_db_path()) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT
                        index_group,
                        index_value AS Value,
                        category AS Category,
                        category_value AS CategoryValue,
                        timestamp AS LocalDateTime,
                        text AS Text
                    FROM accuweather_index_data
                    WHERE location_key = ? AND timestamp = ?
                """,
                    (
                        location_key,
                        timestamp,
                    ),
                )
                rows = cursor.fetchall()
                return self.__parse_query_results([dict(row) for row in rows])

        return await self.hass.async_add_executor_job(query_data)

    @staticmethod
    def __parse_query_results(results: list[dict[str, Any]]) -> dict[str, dict]:
        """Parse the query result."""
        res = {}
        for result in results:
            group = result.pop("index_group")
            res[group] = result

        return res

    async def async_query_index_count(
        self, location_key: str, timestamp: str, data_range: int = 1
    ) -> int:
        """Asynchronously query the count of index data for a location key and timestamp."""

        def query_index_count() -> int:
            with sqlite3.connect(self._get_db_path()) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT COUNT(DISTINCT timestamp)
                    FROM accuweather_index_data
                    WHERE location_key = ? AND
                    timestamp BETWEEN datetime(?, '-1 day') AND datetime(?, ?)
                    """,
                    (location_key, timestamp, timestamp, f"+{data_range - 1} day"),
                )
                return int(cursor.fetchone()[0])

        return await self.hass.async_add_executor_job(query_index_count)
