from __future__ import annotations

import httpx
import pytest

from roamwise.adapters.weather.open_meteo import OpenMeteoWeatherClient
from roamwise.core.models import DateRange, DestinationCandidate


@pytest.mark.asyncio
async def test_open_meteo_client_normalizes_daily_forecast() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["daily"]
        return httpx.Response(
            200,
            json={
                "timezone": "Asia/Shanghai",
                "daily": {
                    "time": ["2026-06-24", "2026-06-25"],
                    "temperature_2m_max": [28.2, 29.1],
                    "temperature_2m_min": [21.0, 22.2],
                    "precipitation_sum": [0.2, 2.4],
                    "precipitation_probability_max": [12, 34],
                    "wind_speed_10m_max": [18.5, 21.0],
                },
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = OpenMeteoWeatherClient(
            http_client=http_client,
            base_url="https://example.test/forecast",
        )
        forecast = await client.fetch_forecast(
            DestinationCandidate(name="杭州", latitude=30.2741, longitude=120.1551),
            DateRange(start="2026-06-24", end="2026-06-25"),
        )

    assert forecast.provider == "Open-Meteo"
    assert len(forecast.daily) == 2
    assert forecast.daily[0].precipitation_probability_max == 12
    assert forecast.evidence[0].fact_type == "weather.forecast.daily"
    assert forecast.evidence[0].fact_value["provider_timezone"] == "Asia/Shanghai"
