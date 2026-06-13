from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from roamwise.core.models import (
    AccessMethod,
    Evidence,
    GeoPoint,
    RouteMode,
    RoutePlan,
    SourceType,
)
from roamwise.core.settings import Settings

AMAP_BASE_URL = "https://restapi.amap.com"


class AmapError(RuntimeError):
    """Raised when Amap returns an application-level error."""


class MissingAmapApiKeyError(AmapError):
    """Raised when AMAP_API_KEY is not configured."""


class AmapClient:
    """Amap Web Service API client for China geocoding and route planning."""

    def __init__(
        self,
        api_key: str | None = None,
        http_client: httpx.AsyncClient | None = None,
        base_url: str = AMAP_BASE_URL,
    ) -> None:
        self._api_key = api_key if api_key is not None else Settings().amap_api_key
        self._client = http_client
        self._base_url = base_url.rstrip("/")

    async def geocode(self, address: str, city: str | None = None) -> GeoPoint:
        params: dict[str, Any] = {"address": address}
        if city:
            params["city"] = city
        payload = await self._get("/v3/geocode/geo", params)
        geocodes = payload.get("geocodes") or []
        if not geocodes:
            raise AmapError(f"Amap geocode returned no result for address: {address}")

        first = geocodes[0]
        longitude, latitude = _parse_location(first["location"])
        return GeoPoint(
            longitude=longitude,
            latitude=latitude,
            label=first.get("formatted_address") or address,
        )

    async def route_driving(self, origin: GeoPoint, destination: GeoPoint) -> RoutePlan:
        params = {
            "origin": origin.amap_location,
            "destination": destination.amap_location,
            "extensions": "base",
        }
        payload = await self._get("/v3/direction/driving", params)
        return self._normalize_driving(origin, destination, params, payload)

    async def route_transit(
        self,
        origin: GeoPoint,
        destination: GeoPoint,
        city: str,
        destination_city: str | None = None,
    ) -> RoutePlan:
        params = {
            "origin": origin.amap_location,
            "destination": destination.amap_location,
            "city": city,
            "extensions": "base",
        }
        if destination_city:
            params["cityd"] = destination_city
        payload = await self._get("/v3/direction/transit/integrated", params)
        return self._normalize_transit(origin, destination, params, payload)

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError)),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self._api_key:
            raise MissingAmapApiKeyError("AMAP_API_KEY is required for Amap Web Service API calls")

        request_params = {"key": self._api_key, "output": "JSON", **params}
        url = f"{self._base_url}{path}"
        if self._client is not None:
            response = await self._client.get(url, params=request_params)
            response.raise_for_status()
            return self._validate_response(response.json())

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, params=request_params)
            response.raise_for_status()
            return self._validate_response(response.json())

    def _validate_response(self, payload: dict[str, Any]) -> dict[str, Any]:
        if payload.get("status") == "1":
            return payload
        info = payload.get("info") or "unknown Amap error"
        infocode = payload.get("infocode")
        raise AmapError(f"Amap API error: {info} ({infocode})")

    def _normalize_driving(
        self,
        origin: GeoPoint,
        destination: GeoPoint,
        query: dict[str, Any],
        payload: dict[str, Any],
    ) -> RoutePlan:
        paths = ((payload.get("route") or {}).get("paths")) or []
        if not paths:
            raise AmapError("Amap driving route returned no path")

        path = paths[0]
        distance = _to_int(path.get("distance"))
        duration_seconds = _to_int(path.get("duration"))
        taxi_cost = _to_float((payload.get("route") or {}).get("taxi_cost"))
        summary = path.get("strategy")
        evidence = self._route_evidence(
            mode=RouteMode.DRIVING,
            query=query,
            payload=payload,
            confidence=0.86,
        )
        return RoutePlan(
            provider="Amap",
            mode=RouteMode.DRIVING,
            origin=origin,
            destination=destination,
            distance_meters=distance,
            duration_minutes=_seconds_to_minutes(duration_seconds),
            cost_estimate=taxi_cost,
            route_summary=summary,
            evidence=[evidence],
        )

    def _normalize_transit(
        self,
        origin: GeoPoint,
        destination: GeoPoint,
        query: dict[str, Any],
        payload: dict[str, Any],
    ) -> RoutePlan:
        route = payload.get("route") or {}
        transits = route.get("transits") or []
        if not transits:
            raise AmapError("Amap transit route returned no transit option")

        transit = transits[0]
        segments = transit.get("segments") or []
        walking_distance = _sum_nested_distance(segments, "walking")
        transfer_count = max(0, len(segments) - 1)
        evidence = self._route_evidence(
            mode=RouteMode.TRANSIT,
            query=query,
            payload=payload,
            confidence=0.82,
        )
        return RoutePlan(
            provider="Amap",
            mode=RouteMode.TRANSIT,
            origin=origin,
            destination=destination,
            distance_meters=_to_int(transit.get("distance")),
            duration_minutes=_seconds_to_minutes(_to_int(transit.get("duration"))),
            transfer_count=transfer_count,
            walking_distance_meters=walking_distance,
            cost_estimate=_to_float(transit.get("cost")),
            route_summary=_transit_summary(segments),
            evidence=[evidence],
        )

    def _route_evidence(
        self,
        mode: RouteMode,
        query: dict[str, Any],
        payload: dict[str, Any],
        confidence: float,
    ) -> Evidence:
        collected_at = datetime.now(UTC)
        return Evidence(
            source_name="Amap",
            source_type=SourceType.FACT,
            access_method=AccessMethod.API,
            query={key: value for key, value in query.items() if key != "key"},
            url_or_reference=f"{self._base_url}/v3/direction/{mode.value}",
            collected_at=collected_at,
            valid_until=collected_at + timedelta(hours=2),
            fact_type=f"route.{mode.value}",
            fact_value=payload,
            confidence=confidence,
            is_factual=True,
            needs_corroboration=False,
        )


def _parse_location(location: str) -> tuple[float, float]:
    longitude_text, latitude_text = location.split(",", maxsplit=1)
    return float(longitude_text), float(latitude_text)


def _to_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(float(value))


def _to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _seconds_to_minutes(seconds: int | None) -> float | None:
    if seconds is None:
        return None
    return round(seconds / 60, 2)


def _sum_nested_distance(segments: list[dict[str, Any]], key: str) -> int:
    total = 0
    for segment in segments:
        nested = segment.get(key) or {}
        total += _to_int(nested.get("distance")) or 0
    return total


def _transit_summary(segments: list[dict[str, Any]]) -> str:
    names: list[str] = []
    for segment in segments:
        buslines = ((segment.get("bus") or {}).get("buslines")) or []
        if buslines:
            name = buslines[0].get("name")
            if name:
                names.append(name)
        railway = segment.get("railway") or {}
        railway_name = railway.get("name")
        if railway_name:
            names.append(railway_name)
    return " -> ".join(names) if names else "transit route"
