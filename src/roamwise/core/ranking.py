from __future__ import annotations

from statistics import mean

from roamwise.core.models import (
    DailyWeather,
    DestinationScore,
    HardFilterResult,
    RankingProfile,
    RouteMode,
    RoutePlan,
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


def score_destination_options(
    forecasts: list[WeatherForecast],
    route_plans_by_candidate: dict[str, list[RoutePlan]],
    profile: RankingProfile,
) -> list[DestinationScore]:
    scores = [
        _score_destination(
            forecast,
            route_plans_by_candidate.get(forecast.candidate.name, []),
            profile,
        )
        for forecast in forecasts
    ]
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


def _score_destination(
    forecast: WeatherForecast,
    route_plans: list[RoutePlan],
    profile: RankingProfile,
) -> DestinationScore:
    weather_filter = _apply_weather_hard_filters(forecast.daily, profile)
    transport_filter = _apply_transport_hard_filters(route_plans, profile)
    hard_filter = HardFilterResult(
        passed=weather_filter.passed and transport_filter.passed,
        reasons=[*weather_filter.reasons, *transport_filter.reasons],
    )
    weather_score = _weather_comfort_score(forecast.daily, profile)
    transport_score = _transport_score(route_plans, profile)
    evidence = [*forecast.evidence, *(item for route in route_plans for item in route.evidence)]
    evidence_quality_score = _combined_evidence_quality_score(evidence)

    if not hard_filter.passed:
        total_score = min((weather_score * 0.2) + (transport_score * 0.15), 35)
    else:
        weights = profile.weights
        weighted_total = (
            weather_score * weights.weather
            + transport_score * weights.transport
            + evidence_quality_score * weights.evidence_quality
        )
        total_score = weighted_total / weights.total if weights.total else 0

    explanation = _build_destination_explanation(
        forecast,
        route_plans,
        hard_filter,
        weather_score,
        transport_score,
        evidence_quality_score,
    )
    return DestinationScore(
        candidate=forecast.candidate,
        hard_filter=hard_filter,
        weather_score=round(weather_score, 2),
        transport_score=round(transport_score, 2),
        evidence_quality_score=round(evidence_quality_score, 2),
        total_score=round(total_score, 2),
        explanation=explanation,
        evidence=evidence,
        route_plans=route_plans,
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


def _apply_transport_hard_filters(
    route_plans: list[RoutePlan],
    profile: RankingProfile,
) -> HardFilterResult:
    policy = profile.transport_policy
    reasons: list[str] = []
    preferred_routes = _preferred_routes(route_plans, profile)
    best_route = _best_route(preferred_routes)

    if policy.no_self_drive and not any(route.mode == RouteMode.TRANSIT for route in route_plans):
        reasons.append("要求不自驾，但未找到公共交通路线")

    if not best_route:
        reasons.append("未找到符合偏好交通方式的路线")
        return HardFilterResult(passed=False, reasons=reasons)

    if (
        policy.max_total_travel_minutes is not None
        and best_route.duration_minutes is not None
        and best_route.duration_minutes > policy.max_total_travel_minutes
    ):
        reasons.append(
            f"交通耗时 {best_route.duration_minutes:.0f} 分钟超过限制 "
            f"{policy.max_total_travel_minutes} 分钟"
        )

    if (
        policy.max_transfer_count is not None
        and best_route.transfer_count is not None
        and best_route.transfer_count > policy.max_transfer_count
    ):
        reasons.append(
            f"换乘次数 {best_route.transfer_count} 次超过限制 {policy.max_transfer_count} 次"
        )

    if (
        policy.max_walking_distance_meters is not None
        and best_route.walking_distance_meters is not None
        and best_route.walking_distance_meters > policy.max_walking_distance_meters
    ):
        reasons.append(
            f"步行距离 {best_route.walking_distance_meters} 米超过限制 "
            f"{policy.max_walking_distance_meters} 米"
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


def _transport_score(route_plans: list[RoutePlan], profile: RankingProfile) -> float:
    route = _best_route(_preferred_routes(route_plans, profile))
    if route is None:
        return 0

    score = 100.0
    if route.duration_minutes is not None:
        score -= max(0, route.duration_minutes - 90) * 0.22
    if route.transfer_count is not None:
        score -= route.transfer_count * 6
    if route.walking_distance_meters is not None:
        score -= max(0, route.walking_distance_meters - 800) * 0.01
    if route.mode == RouteMode.DRIVING and profile.transport_policy.no_self_drive:
        score -= 70
    return max(0, min(100, score))


def _preferred_routes(route_plans: list[RoutePlan], profile: RankingProfile) -> list[RoutePlan]:
    preferred_modes = set(profile.transport_policy.preferred_modes)
    if not preferred_modes:
        return route_plans
    return [route for route in route_plans if route.mode in preferred_modes]


def _best_route(route_plans: list[RoutePlan]) -> RoutePlan | None:
    if not route_plans:
        return None
    return min(route_plans, key=lambda route: route.duration_minutes or float("inf"))


def _evidence_quality_score(forecast: WeatherForecast) -> float:
    if not forecast.evidence:
        return 0
    return max(0, min(100, mean(evidence.confidence for evidence in forecast.evidence) * 100))


def _combined_evidence_quality_score(evidence: list) -> float:
    if not evidence:
        return 0
    return max(0, min(100, mean(item.confidence for item in evidence) * 100))


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


def _build_destination_explanation(
    forecast: WeatherForecast,
    route_plans: list[RoutePlan],
    hard_filter: HardFilterResult,
    weather_score: float,
    transport_score: float,
    evidence_quality_score: float,
) -> str:
    weather_text = _build_explanation(
        forecast,
        hard_filter,
        weather_score,
        evidence_quality_score,
    )
    route = _best_route(route_plans)
    if not route:
        return f"{weather_text} 未找到路线数据；交通分 {transport_score:.1f}。"

    duration = "未知" if route.duration_minutes is None else f"{route.duration_minutes:.0f} 分钟"
    transfers = "未知" if route.transfer_count is None else f"{route.transfer_count} 次"
    return (
        f"{weather_text} 交通分 {transport_score:.1f}；"
        f"{route.mode.value} 路线约 {duration}，换乘 {transfers}。"
    )
