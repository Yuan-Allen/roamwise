from __future__ import annotations

from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class AccessMethod(StrEnum):
    API = "api"
    MCP = "mcp"
    CLI = "cli"
    BROWSER = "browser"
    SEARCH = "search"
    MANUAL = "manual"


class SourceType(StrEnum):
    FACT = "fact"
    CONTEXT = "context"
    INSPIRATION = "inspiration"
    OFFICIAL = "official"


class DateRange(BaseModel):
    start: date
    end: date

    @model_validator(mode="after")
    def validate_order(self) -> DateRange:
        if self.end < self.start:
            raise ValueError("date_range.end must be on or after date_range.start")
        return self


class DestinationCandidate(BaseModel):
    name: str
    country_or_region: str | None = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    themes: list[str] = Field(default_factory=list)


class GeoPoint(BaseModel):
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(ge=-90, le=90)
    label: str | None = None

    @property
    def amap_location(self) -> str:
        return f"{self.longitude},{self.latitude}"


class WeatherPolicy(BaseModel):
    max_precipitation_probability: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Hard filter: maximum allowed daily precipitation probability.",
    )
    max_precipitation_sum_mm: float | None = Field(
        default=None,
        ge=0,
        description="Hard filter: maximum allowed daily precipitation amount.",
    )
    min_temperature_c: float | None = None
    max_temperature_c: float | None = None
    ideal_min_temperature_c: float = 12
    ideal_max_temperature_c: float = 26

    @model_validator(mode="after")
    def validate_temperature_bounds(self) -> WeatherPolicy:
        if (
            self.min_temperature_c is not None
            and self.max_temperature_c is not None
            and self.max_temperature_c < self.min_temperature_c
        ):
            raise ValueError("max_temperature_c must be greater than or equal to min_temperature_c")
        if self.ideal_max_temperature_c < self.ideal_min_temperature_c:
            raise ValueError("ideal_max_temperature_c must be >= ideal_min_temperature_c")
        return self


class RankingWeights(BaseModel):
    weather: float = Field(default=1.0, ge=0)
    transport: float = Field(default=0.0, ge=0)
    evidence_quality: float = Field(default=0.2, ge=0)

    @property
    def total(self) -> float:
        return self.weather + self.transport + self.evidence_quality


class RouteMode(StrEnum):
    DRIVING = "driving"
    TRANSIT = "transit"
    WALKING = "walking"
    BICYCLING = "bicycling"


class TransportPolicy(BaseModel):
    no_self_drive: bool = False
    preferred_modes: list[RouteMode] = Field(default_factory=lambda: [RouteMode.TRANSIT])
    max_total_travel_minutes: int | None = Field(default=None, ge=0)
    max_transfer_count: int | None = Field(default=None, ge=0)
    max_walking_distance_meters: int | None = Field(default=None, ge=0)


class RankingProfile(BaseModel):
    name: str = "default"
    hard_filters: list[str] = Field(default_factory=list)
    weather_policy: WeatherPolicy = Field(default_factory=WeatherPolicy)
    transport_policy: TransportPolicy = Field(default_factory=TransportPolicy)
    weights: RankingWeights = Field(default_factory=RankingWeights)


class TravelRequest(BaseModel):
    origin: str
    date_range: DateRange
    candidates: list[DestinationCandidate] = Field(default_factory=list)
    ranking_profile: RankingProfile = Field(default_factory=RankingProfile)
    locale: str = "zh-CN"
    notes: str | None = None


class Evidence(BaseModel):
    source_name: str
    source_type: SourceType
    access_method: AccessMethod
    query: dict[str, Any] = Field(default_factory=dict)
    url_or_reference: str
    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    valid_until: datetime | None = None
    fact_type: str
    fact_value: dict[str, Any]
    confidence: float = Field(ge=0, le=1)
    is_factual: bool = True
    needs_corroboration: bool = False


class DailyWeather(BaseModel):
    date: date
    temperature_max_c: float | None = None
    temperature_min_c: float | None = None
    precipitation_sum_mm: float | None = None
    precipitation_probability_max: int | None = Field(default=None, ge=0, le=100)
    wind_speed_max_kmh: float | None = None


class WeatherForecast(BaseModel):
    candidate: DestinationCandidate
    provider: str
    daily: list[DailyWeather]
    evidence: list[Evidence]

    @field_validator("daily")
    @classmethod
    def require_daily_weather(cls, daily: list[DailyWeather]) -> list[DailyWeather]:
        if not daily:
            raise ValueError("weather forecast must include at least one daily record")
        return daily


class RoutePlan(BaseModel):
    provider: str
    mode: RouteMode
    origin: GeoPoint
    destination: GeoPoint
    distance_meters: int | None = Field(default=None, ge=0)
    duration_minutes: float | None = Field(default=None, ge=0)
    transfer_count: int | None = Field(default=None, ge=0)
    walking_distance_meters: int | None = Field(default=None, ge=0)
    cost_estimate: float | None = Field(default=None, ge=0)
    route_summary: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)


class ContentResearchQuery(BaseModel):
    query: str
    origin: str | None = None
    destination_names: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)
    limit: int = Field(default=10, ge=1, le=50)


class ContentMention(BaseModel):
    destination_name: str
    source_name: str
    source_type: SourceType = SourceType.INSPIRATION
    access_method: AccessMethod
    title: str
    url_or_reference: str
    summary: str
    themes: list[str] = Field(default_factory=list)
    itinerary_patterns: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class ContentResearchResult(BaseModel):
    query: ContentResearchQuery
    mentions: list[ContentMention]
    evidence: list[Evidence] = Field(default_factory=list)


class HardFilterResult(BaseModel):
    passed: bool
    reasons: list[str] = Field(default_factory=list)


class DestinationScore(BaseModel):
    candidate: DestinationCandidate
    hard_filter: HardFilterResult
    weather_score: float = Field(ge=0, le=100)
    transport_score: float = Field(default=0, ge=0, le=100)
    evidence_quality_score: float = Field(ge=0, le=100)
    total_score: float = Field(ge=0, le=100)
    explanation: str
    evidence: list[Evidence] = Field(default_factory=list)
    route_plans: list[RoutePlan] = Field(default_factory=list)


class RecommendationResult(BaseModel):
    request: TravelRequest
    scores: list[DestinationScore]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
