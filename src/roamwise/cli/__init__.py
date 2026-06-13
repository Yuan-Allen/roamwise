from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Annotated

import typer
from pydantic import TypeAdapter
from rich.console import Console

from roamwise.adapters.weather import OpenMeteoWeatherClient
from roamwise.core.models import RecommendationResult, TravelRequest
from roamwise.core.ranking import score_weather_forecasts
from roamwise.core.reports import recommendation_to_markdown

app = typer.Typer(help="Roamwise travel research commands.")
recommend_app = typer.Typer(help="Generate recommendation reports.")
app.add_typer(recommend_app, name="recommend")
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


async def _recommend_weather(request_path: Path) -> RecommendationResult:
    request = _load_request(request_path)
    client = OpenMeteoWeatherClient()
    forecasts = [
        await client.fetch_forecast(candidate, request.date_range)
        for candidate in request.candidates
    ]
    scores = score_weather_forecasts(forecasts, request.ranking_profile)
    return RecommendationResult(request=request, scores=scores)


def _load_request(path: Path) -> TravelRequest:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return TypeAdapter(TravelRequest).validate_python(payload)
