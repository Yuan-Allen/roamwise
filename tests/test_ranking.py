from __future__ import annotations

from roamwise.core.models import (
    AccessMethod,
    DailyWeather,
    DestinationCandidate,
    Evidence,
    RankingProfile,
    SourceType,
    WeatherForecast,
    WeatherPolicy,
)
from roamwise.core.ranking import score_weather_forecasts


def test_weather_ranking_applies_rain_hard_filter() -> None:
    profile = RankingProfile(
        name="rain-first",
        weather_policy=WeatherPolicy(
            max_precipitation_probability=40,
            max_precipitation_sum_mm=5,
            ideal_min_temperature_c=16,
            ideal_max_temperature_c=28,
        ),
    )

    dry = _forecast("青岛", probability=20, precipitation=1.0)
    wet = _forecast("杭州", probability=80, precipitation=12.0)

    scores = score_weather_forecasts([wet, dry], profile)

    assert scores[0].candidate.name == "青岛"
    assert scores[0].hard_filter.passed is True
    assert scores[1].candidate.name == "杭州"
    assert scores[1].hard_filter.passed is False
    assert "最高降水概率" in scores[1].hard_filter.reasons[0]


def _forecast(name: str, probability: int, precipitation: float) -> WeatherForecast:
    candidate = DestinationCandidate(name=name, latitude=1, longitude=2)
    return WeatherForecast(
        candidate=candidate,
        provider="test",
        daily=[
            DailyWeather(
                date="2026-06-24",
                temperature_max_c=26,
                temperature_min_c=18,
                precipitation_sum_mm=precipitation,
                precipitation_probability_max=probability,
                wind_speed_max_kmh=10,
            )
        ],
        evidence=[
            Evidence(
                source_name="test",
                source_type=SourceType.FACT,
                access_method=AccessMethod.API,
                url_or_reference="https://example.test",
                fact_type="weather.forecast.daily",
                fact_value={},
                confidence=0.9,
            )
        ],
    )
