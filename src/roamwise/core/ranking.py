from __future__ import annotations

from statistics import mean

from roamwise.core.models import (
    DailyWeather,
    DestinationScore,
    HardFilterResult,
    RankingProfile,
    WeatherForecast,
)


def score_weather_forecasts(
    forecasts: list[WeatherForecast],
    profile: RankingProfile,
) -> list[DestinationScore]:
    scores = [_score_forecast(forecast, profile) for forecast in forecasts]
    return sorted(
        scores,
        key=lambda score: (score.hard_filter.passed, score.total_score),
        reverse=True,
    )


def _score_forecast(forecast: WeatherForecast, profile: RankingProfile) -> DestinationScore:
    hard_filter = _apply_weather_hard_filters(forecast.daily, profile)
    weather_score = _weather_comfort_score(forecast.daily, profile)
    evidence_quality_score = _evidence_quality_score(forecast)

    if not hard_filter.passed:
        total_score = min(weather_score * 0.25, 30)
    else:
        weights = profile.weights
        weighted_total = (
            weather_score * weights.weather + evidence_quality_score * weights.evidence_quality
        )
        total_score = weighted_total / weights.total if weights.total else 0

    explanation = _build_explanation(forecast, hard_filter, weather_score, evidence_quality_score)

    return DestinationScore(
        candidate=forecast.candidate,
        hard_filter=hard_filter,
        weather_score=round(weather_score, 2),
        evidence_quality_score=round(evidence_quality_score, 2),
        total_score=round(total_score, 2),
        explanation=explanation,
        evidence=forecast.evidence,
    )


def _apply_weather_hard_filters(
    daily: list[DailyWeather],
    profile: RankingProfile,
) -> HardFilterResult:
    policy = profile.weather_policy
    reasons: list[str] = []

    if policy.max_precipitation_probability is not None:
        max_probability = max(
            (day.precipitation_probability_max or 0 for day in daily),
            default=0,
        )
        if max_probability > policy.max_precipitation_probability:
            reasons.append(
                f"最高降水概率 {max_probability}% 超过限制 {policy.max_precipitation_probability}%"
            )

    if policy.max_precipitation_sum_mm is not None:
        max_precipitation = max((day.precipitation_sum_mm or 0 for day in daily), default=0)
        if max_precipitation > policy.max_precipitation_sum_mm:
            reasons.append(
                f"单日最高降水量 {max_precipitation:.1f}mm 超过限制 "
                f"{policy.max_precipitation_sum_mm:.1f}mm"
            )

    if policy.min_temperature_c is not None:
        min_temperature = min(
            (day.temperature_min_c for day in daily if day.temperature_min_c is not None),
            default=None,
        )
        if min_temperature is not None and min_temperature < policy.min_temperature_c:
            reasons.append(
                f"最低气温 {min_temperature:.1f}C 低于限制 {policy.min_temperature_c:.1f}C"
            )

    if policy.max_temperature_c is not None:
        max_temperature = max(
            (day.temperature_max_c for day in daily if day.temperature_max_c is not None),
            default=None,
        )
        if max_temperature is not None and max_temperature > policy.max_temperature_c:
            reasons.append(
                f"最高气温 {max_temperature:.1f}C 高于限制 {policy.max_temperature_c:.1f}C"
            )

    return HardFilterResult(passed=not reasons, reasons=reasons)


def _weather_comfort_score(daily: list[DailyWeather], profile: RankingProfile) -> float:
    policy = profile.weather_policy
    day_scores = [
        _daily_weather_score(day, policy.ideal_min_temperature_c, policy.ideal_max_temperature_c)
        for day in daily
    ]
    return max(0, min(100, mean(day_scores) if day_scores else 0))


def _daily_weather_score(
    day: DailyWeather,
    ideal_min_temperature_c: float,
    ideal_max_temperature_c: float,
) -> float:
    score = 100.0

    probability = day.precipitation_probability_max
    if probability is not None:
        score -= probability * 0.45

    precipitation = day.precipitation_sum_mm
    if precipitation is not None:
        score -= min(35, precipitation * 4)

    if day.temperature_max_c is not None:
        if day.temperature_max_c > ideal_max_temperature_c:
            score -= (day.temperature_max_c - ideal_max_temperature_c) * 3
        elif day.temperature_max_c < ideal_min_temperature_c:
            score -= (ideal_min_temperature_c - day.temperature_max_c) * 2

    if day.temperature_min_c is not None and day.temperature_min_c < ideal_min_temperature_c - 8:
        score -= (ideal_min_temperature_c - 8 - day.temperature_min_c) * 1.5

    if day.wind_speed_max_kmh is not None and day.wind_speed_max_kmh > 35:
        score -= min(20, (day.wind_speed_max_kmh - 35) * 0.8)

    return max(0, min(100, score))


def _evidence_quality_score(forecast: WeatherForecast) -> float:
    if not forecast.evidence:
        return 0
    return max(0, min(100, mean(evidence.confidence for evidence in forecast.evidence) * 100))


def _build_explanation(
    forecast: WeatherForecast,
    hard_filter: HardFilterResult,
    weather_score: float,
    evidence_quality_score: float,
) -> str:
    max_probability = max(
        (day.precipitation_probability_max or 0 for day in forecast.daily),
        default=0,
    )
    max_precipitation = max((day.precipitation_sum_mm or 0 for day in forecast.daily), default=0)
    max_temperature = max(
        (day.temperature_max_c for day in forecast.daily if day.temperature_max_c is not None),
        default=None,
    )

    status = "通过硬过滤" if hard_filter.passed else "未通过硬过滤"
    temperature_text = "未知" if max_temperature is None else f"{max_temperature:.1f}C"
    return (
        f"{status}；天气分 {weather_score:.1f}，证据质量 {evidence_quality_score:.1f}。"
        f"最高降水概率 {max_probability}%，单日最高降水量 {max_precipitation:.1f}mm，"
        f"最高气温 {temperature_text}。"
    )
