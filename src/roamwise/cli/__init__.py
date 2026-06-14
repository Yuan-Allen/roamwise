from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Annotated

import typer
from pydantic import TypeAdapter
from rich.console import Console

from roamwise.adapters.content import LocalContentSeedAdapter
from roamwise.adapters.maps import AmapClient, AmapError, MissingAmapApiKeyError
from roamwise.adapters.weather import OpenMeteoWeatherClient
from roamwise.core.candidates import ensure_candidates
from roamwise.core.models import (
    ContentResearchQuery,
    GeoPoint,
    RecommendationResult,
    RouteMode,
    RoutePlan,
    TravelRequest,
)
from roamwise.core.ranking import score_destination_options, score_weather_forecasts
from roamwise.core.reports import (
    destination_recommendation_to_markdown,
    recommendation_to_markdown,
)

app = typer.Typer(help="Roamwise travel research commands.")
recommend_app = typer.Typer(help="Generate recommendation reports.")
amap_app = typer.Typer(help="Inspect Amap Web Service API access.")
content_app = typer.Typer(help="Research social and guide inspiration sources.")
app.add_typer(recommend_app, name="recommend")
app.add_typer(amap_app, name="amap")
app.add_typer(content_app, name="content")
console = Console()


@recommend_app.command("weather")
def recommend_weather(
    request_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to a TravelRequest JSON file.",
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Optional path for the rendered report."),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Emit structured JSON instead of Markdown."),
    ] = False,
) -> None:
    """Rank candidate destinations by weather using Open-Meteo."""

    result = asyncio.run(_recommend_weather(request_path))
    if json_output:
        rendered = result.model_dump_json(indent=2)
    else:
        rendered = recommendation_to_markdown(result)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        console.print(f"Wrote {output}")
    else:
        console.print(rendered)


@recommend_app.command("destination")
def recommend_destination(
    request_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to a TravelRequest JSON file.",
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Optional path for the rendered report."),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Emit structured JSON instead of Markdown."),
    ] = False,
) -> None:
    """Rank destinations by weather and Amap route feasibility."""

    try:
        result = asyncio.run(_recommend_destination(request_path))
    except MissingAmapApiKeyError as exc:
        raise typer.BadParameter(str(exc), param_hint="AMAP_API_KEY") from exc

    if json_output:
        rendered = result.model_dump_json(indent=2)
    else:
        rendered = destination_recommendation_to_markdown(result)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        console.print(f"Wrote {output}")
    else:
        console.print(rendered)


async def _recommend_weather(request_path: Path) -> RecommendationResult:
    request = _load_request(request_path)
    if not request.candidates:
        raise typer.BadParameter(
            "weather recommendation requires explicit candidates",
            param_hint="candidates",
        )
    client = OpenMeteoWeatherClient()
    forecasts = [
        await client.fetch_forecast(candidate, request.date_range)
        for candidate in request.candidates
    ]
    scores = score_weather_forecasts(forecasts, request.ranking_profile)
    return RecommendationResult(request=request, scores=scores)


async def _recommend_destination(request_path: Path) -> RecommendationResult:
    request = ensure_candidates(_load_request(request_path))
    weather_client = OpenMeteoWeatherClient()
    amap_client = AmapClient()
    origin = await amap_client.geocode(request.origin)

    forecasts = []
    route_plans_by_candidate: dict[str, list[RoutePlan]] = {}
    for candidate in request.candidates:
        forecasts.append(await weather_client.fetch_forecast(candidate, request.date_range))
        destination = GeoPoint(
            longitude=candidate.longitude,
            latitude=candidate.latitude,
            label=candidate.name,
        )
        route_plans_by_candidate[candidate.name] = await _collect_amap_routes(
            amap_client,
            origin,
            destination,
            request.origin,
            candidate.name,
            request.ranking_profile.transport_policy.preferred_modes,
        )

    scores = score_destination_options(
        forecasts,
        route_plans_by_candidate,
        request.ranking_profile,
    )
    return RecommendationResult(request=request, scores=scores)


async def _collect_amap_routes(
    amap_client: AmapClient,
    origin: GeoPoint,
    destination: GeoPoint,
    origin_city: str,
    destination_city: str,
    preferred_modes: list[RouteMode],
) -> list[RoutePlan]:
    routes: list[RoutePlan] = []
    if RouteMode.TRANSIT in preferred_modes:
        try:
            routes.append(
                await amap_client.route_transit(
                    origin,
                    destination,
                    city=origin_city,
                    destination_city=destination_city,
                )
            )
        except AmapError:
            pass
    if RouteMode.DRIVING in preferred_modes:
        try:
            routes.append(await amap_client.route_driving(origin, destination))
        except AmapError:
            pass
    return routes


def _load_request(path: Path) -> TravelRequest:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return TypeAdapter(TravelRequest).validate_python(payload)


@content_app.command("seed")
def content_seed(
    request_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to a TravelRequest JSON file.",
        ),
    ],
    limit: Annotated[int, typer.Option("--limit", "-n", min=1, max=50)] = 10,
) -> None:
    """Return local structured inspiration mentions for a request.

    This is a scaffold command. It fixes the output contract that future
    Xiaohongshu, Zhihu, Trip.com, search, MCP, or OpenCLI adapters should match.
    """

    request = ensure_candidates(_load_request(request_path), limit=limit)
    query = ContentResearchQuery(
        query=_content_query_text(request),
        origin=request.origin,
        destination_names=[candidate.name for candidate in request.candidates],
        themes=_request_themes(request),
        limit=limit,
    )
    result = asyncio.run(LocalContentSeedAdapter().research(query))
    console.print(result.model_dump_json(indent=2))


@amap_app.command("geocode")
def amap_geocode(
    address: Annotated[str, typer.Argument(help="Address or place name to geocode.")],
    city: Annotated[str | None, typer.Option("--city", help="Optional city hint.")] = None,
) -> None:
    """Resolve an address to an Amap coordinate."""

    try:
        point = asyncio.run(AmapClient().geocode(address=address, city=city))
    except MissingAmapApiKeyError as exc:
        raise typer.BadParameter(str(exc), param_hint="AMAP_API_KEY") from exc
    except AmapError as exc:
        raise typer.ClickException(str(exc)) from exc
    console.print(point.model_dump_json(indent=2))


@amap_app.command("driving")
def amap_driving(
    origin: Annotated[str, typer.Argument(help="Origin coordinate as longitude,latitude.")],
    destination: Annotated[
        str, typer.Argument(help="Destination coordinate as longitude,latitude.")
    ],
) -> None:
    """Fetch a driving route from Amap."""

    try:
        origin_point = _parse_cli_point(origin)
        destination_point = _parse_cli_point(destination)
        route = asyncio.run(AmapClient().route_driving(origin_point, destination_point))
    except MissingAmapApiKeyError as exc:
        raise typer.BadParameter(str(exc), param_hint="AMAP_API_KEY") from exc
    except AmapError as exc:
        raise typer.ClickException(str(exc)) from exc
    console.print(route.model_dump_json(indent=2))


def _parse_cli_point(raw: str) -> GeoPoint:
    try:
        longitude_text, latitude_text = raw.split(",", maxsplit=1)
        return GeoPoint(longitude=float(longitude_text), latitude=float(latitude_text))
    except ValueError as exc:
        raise typer.BadParameter("coordinate must be formatted as longitude,latitude") from exc


def _content_query_text(request: TravelRequest) -> str:
    parts = [request.origin, request.notes or "", request.ranking_profile.name]
    return " ".join(part for part in parts if part).strip()


def _request_themes(request: TravelRequest) -> list[str]:
    themes: list[str] = []
    for candidate in request.candidates:
        for theme in candidate.themes:
            if theme not in themes:
                themes.append(theme)
    return themes
