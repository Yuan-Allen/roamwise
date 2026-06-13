from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

from roamwise.core.models import DestinationCandidate, TravelRequest

CITY_SEEDS: list[DestinationCandidate] = [
    DestinationCandidate(
        name="杭州",
        country_or_region="中国",
        latitude=30.2741,
        longitude=120.1551,
        themes=["西湖", "城市短途", "美食"],
    ),
    DestinationCandidate(
        name="苏州",
        country_or_region="中国",
        latitude=31.2989,
        longitude=120.5853,
        themes=["园林", "古城", "高铁"],
    ),
    DestinationCandidate(
        name="南京",
        country_or_region="中国",
        latitude=32.0603,
        longitude=118.7969,
        themes=["历史", "博物馆", "美食"],
    ),
    DestinationCandidate(
        name="宁波",
        country_or_region="中国",
        latitude=29.8683,
        longitude=121.544,
        themes=["海鲜", "港口", "城市"],
    ),
    DestinationCandidate(
        name="无锡",
        country_or_region="中国",
        latitude=31.4912,
        longitude=120.3119,
        themes=["太湖", "短途", "美食"],
    ),
    DestinationCandidate(
        name="绍兴",
        country_or_region="中国",
        latitude=30.0303,
        longitude=120.5802,
        themes=["古城", "黄酒", "文化"],
    ),
    DestinationCandidate(
        name="黄山",
        country_or_region="中国",
        latitude=29.7147,
        longitude=118.3376,
        themes=["山景", "徒步", "自然"],
    ),
    DestinationCandidate(
        name="青岛",
        country_or_region="中国",
        latitude=36.0671,
        longitude=120.3826,
        themes=["海边", "啤酒", "避暑"],
    ),
    DestinationCandidate(
        name="厦门",
        country_or_region="中国",
        latitude=24.4798,
        longitude=118.0894,
        themes=["海岛", "美食", "城市"],
    ),
    DestinationCandidate(
        name="长沙",
        country_or_region="中国",
        latitude=28.2282,
        longitude=112.9388,
        themes=["美食", "夜生活", "城市"],
    ),
]

ORIGIN_POINTS: dict[str, tuple[float, float]] = {
    "上海": (31.2304, 121.4737),
    "北京": (39.9042, 116.4074),
    "广州": (23.1291, 113.2644),
    "深圳": (22.5431, 114.0579),
    "杭州": (30.2741, 120.1551),
}


def ensure_candidates(request: TravelRequest, limit: int = 6) -> TravelRequest:
    if request.candidates:
        return request

    generated = generate_candidates(origin=request.origin, limit=limit)
    return request.model_copy(update={"candidates": generated})


def generate_candidates(origin: str, limit: int = 6) -> list[DestinationCandidate]:
    origin_point = ORIGIN_POINTS.get(origin)
    if origin_point is None:
        return CITY_SEEDS[:limit]

    origin_latitude, origin_longitude = origin_point
    ranked = sorted(
        (
            (
                _haversine_km(
                    origin_latitude,
                    origin_longitude,
                    candidate.latitude,
                    candidate.longitude,
                ),
                candidate,
            )
            for candidate in CITY_SEEDS
            if candidate.name != origin
        ),
        key=lambda item: item[0],
    )
    return [candidate for _, candidate in ranked[:limit]]


def _haversine_km(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    radius_km = 6371.0
    delta_latitude = radians(latitude_b - latitude_a)
    delta_longitude = radians(longitude_b - longitude_a)
    a = (
        sin(delta_latitude / 2) ** 2
        + cos(radians(latitude_a)) * cos(radians(latitude_b)) * sin(delta_longitude / 2) ** 2
    )
    return 2 * radius_km * asin(sqrt(a))
