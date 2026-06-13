from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from roamwise.core.models import (
    AccessMethod,
    DailyWeather,
    DateRange,
    DestinationCandidate,
    Evidence,
    SourceType,
    WeatherForecast,
)

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "precipitation_probability_max",
    "wind_speed_10m_max",
]


class OpenMeteoWeatherClient:
    """Open-Meteo forecast client.

    The free forecast endpoint is a useful first provider because it supports global
    coordinates and does not require an API key for basic use.
    """

    def __init__(
        self,
        http_client: httpx.AsyncClient | None = None,
        base_url: str = OPEN_METEO_FORECAST_URL,
    ) -> None:
        self._client = http_client
        self._base_url = base_url

    async def fetch_forecast(
        self,
        candidate: DestinationCandidate,
        date_range: DateRange,
    ) -> WeatherForecast:
        params = self._build_params(candidate, date_range)
        payload = await self._get(params)
        return self._normalize(candidate, params, payload)

    def _build_params(
        self,
        candidate: DestinationCandidate,
        date_range: DateRange,
    ) -> dict[str, Any]:
        return {
            "latitude": candidate.latitude,
            "longitude": candidate.longitude,
            "daily": ",".join(DAILY_VARIABLES),
            "timezone": "auto",
            "start_date": date_range.start.isoformat(),
            "end_date": date_range.end.isoformat(),
        }

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError)),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _get(self, params: dict[str, Any]) -> dict[str, Any]:
        if self._client is not None:
            response = await self._client.get(self._base_url, params=params)
            response.raise_for_status()
            return response.json()

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(self._base_url, params=params)
            response.raise_for_status()
            return response.json()

    def _normalize(
        self,
        candidate: DestinationCandidate,
        query: dict[str, Any],
        payload: dict[str, Any],
    ) -> WeatherForecast:
        daily_payload = payload.get("daily") or {}
        dates = daily_payload.get("time") or []
        collected_at = datetime.now(UTC)

        daily_records = [
            DailyWeather(
                date=day,
                temperature_max_c=self._value_at(daily_payload, "temperature_2m_max", index),
                temperature_min_c=self._value_at(daily_payload, "temperature_2m_min", index),
                precipitation_sum_mm=self._value_at(daily_payload, "precipitation_sum", index),
                precipitation_probability_max=self._value_at(
                    daily_payload,
                    "precipitation_probability_max",
                    index,
                ),
                wind_speed_max_kmh=self._value_at(daily_payload, "wind_speed_10m_max", index),
            )
            for index, day in enumerate(dates)
        ]

        evidence = Evidence(
            source_name="Open-Meteo",
            source_type=SourceType.FACT,
            access_method=AccessMethod.API,
            query=query,
            url_or_reference=self._base_url,
            collected_at=collected_at,
            valid_until=collected_at + timedelta(hours=6),
            fact_type="weather.forecast.daily",
            fact_value={
                "candidate": candidate.model_dump(),
                "daily": [record.model_dump(mode="json") for record in daily_records],
                "provider_timezone": payload.get("timezone"),
            },
            confidence=0.82,
            is_factual=True,
            needs_corroboration=False,
        )

        return WeatherForecast(
            candidate=candidate,
            provider="Open-Meteo",
            daily=daily_records,
            evidence=[evidence],
        )

    @staticmethod
    def _value_at(payload: dict[str, Any], key: str, index: int) -> Any:
        values = payload.get(key) or []
        if index >= len(values):
            return None
        return values[index]
