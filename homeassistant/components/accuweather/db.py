import sqlite3
import logging
import datetime
from typing import Any, List, Dict
from typing import Any
import uuid

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class AccuWeatherIndexGroupDataStore:
    """Class to handle the index data store."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the index data store."""
        self.hass = hass
        _LOGGER.info("AccuWeatherIndexGroupDataStore initialized.")

    def _get_db_path(self) -> str:
        """Get the database path."""
        db_path = self.hass.config.path("home-assistant_v2.db")
        _LOGGER.debug("Database path resolved: %s", db_path)
        return db_path

    async def async_create_index_data_table(self) -> None:
        """Asynchronously create the index data table if it doesn't exist."""
        _LOGGER.info("Creating index data table...")

        def create_table() -> None:
            try:
                with sqlite3.connect(self._get_db_path()) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS accuweather_index_data (
                            id TEXT PRIMARY KEY,
                            location_key TEXT NOT NULL,
                            index_group TEXT NOT NULL,
                            index_value INT NOT NULL,
                            category TEXT NOT NULL,
                            category_value INT NOT NULL,
                            timestamp DATETIME NOT NULL,
                            text TEXT NOT NULL,
                            UNIQUE (location_key, index_group, timestamp) ON CONFLICT REPLACE
                        )
                    """)
                    conn.commit()
                    _LOGGER.info("Index data table created successfully.")
            except sqlite3.Error as e:
                _LOGGER.error("Error creating index data table: %s", e)

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
        _LOGGER.info(
            "Inserting data for location_key=%s, index_group=%s...",
            location_key,
            index_group,
        )

        def insert_data() -> None:
            try:
                with sqlite3.connect(self._get_db_path()) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO accuweather_index_data (
                            id,
                            location_key,
                            index_group,
                            index_value,
                            category,
                            category_value,
                            timestamp,
                            text
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            str(uuid.uuid4()),
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
                    _LOGGER.info(
                        "Data inserted for location_key=%s, index_group=%s.",
                        location_key,
                        index_group,
                    )
            except sqlite3.Error as e:
                _LOGGER.error("Error inserting data: %s", e)

        await self.hass.async_add_executor_job(insert_data)

    async def async_query_data(
        self, location_key: str, timestamp: str
    ) -> dict[str, dict]:
        """Asynchronously query data by index group and timestamp."""
        _LOGGER.info(
            "Querying data for location_key=%s, timestamp=%s...",
            location_key,
            timestamp,
        )

        def query_data() -> dict[str, dict]:
            try:
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
                        (location_key, timestamp),
                    )
                    rows = cursor.fetchall()
                    _LOGGER.debug("Query returned %d rows.", len(rows))
                    return self.__parse_query_results([dict(row) for row in rows])
            except sqlite3.Error as e:
                _LOGGER.error("Error querying data: %s", e)
                return {}

        return await self.hass.async_add_executor_job(query_data)

    async def async_query_data_range(
        self, location_key: str, start_date: str, end_date: str
    ) -> list[dict[str, Any]]:
        """Asynchronously query data for a range of dates."""
        _LOGGER.info(
            "Querying data range for location_key=%s, start_date=%s, end_date=%s...",
            location_key,
            start_date,
            end_date,
        )

        def query_data_range() -> list[dict[str, Any]]:
            try:
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
                        WHERE location_key = ? AND
                            timestamp BETWEEN ? AND ?
                        ORDER BY timestamp ASC
                        """,
                        (location_key, start_date, end_date),
                    )
                    rows = cursor.fetchall()
                    _LOGGER.debug("Range query returned %d rows.", len(rows))
                    return [dict(row) for row in rows]
            except sqlite3.Error as e:
                _LOGGER.error("Error querying data range: %s", e)
                return []

        return await self.hass.async_add_executor_job(query_data_range)

    @staticmethod
    def __parse_query_results(results: list[dict[str, Any]]) -> dict[str, dict]:
        """Parse the query result."""
        res = {}
        for result in results:
            group = result.pop("index_group")
            res[group] = result

        _LOGGER.debug("Parsed query results: %s", res)
        return res

    async def async_query_index_count(
        self, location_key: str, timestamp: str, data_range: int = 1
    ) -> int:
        """Asynchronously query the count of index data for a location key and timestamp."""
        _LOGGER.info(
            "Querying index count for location_key=%s, timestamp=%s, data_range=%d...",
            location_key,
            timestamp,
            data_range,
        )

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
