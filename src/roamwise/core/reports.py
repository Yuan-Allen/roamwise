from __future__ import annotations

from roamwise.core.models import RecommendationResult


def recommendation_to_markdown(result: RecommendationResult) -> str:
    request = result.request
    lines = [
        "# Roamwise Weather Recommendation",
        "",
        f"- Origin: {request.origin}",
        f"- Dates: {request.date_range.start.isoformat()} to {request.date_range.end.isoformat()}",
        f"- Profile: {request.ranking_profile.name}",
        f"- Generated at: {result.generated_at.isoformat()}",
        "",
        "## Ranked Destinations",
        "",
        "| Rank | Destination | Status | Total | Weather | Evidence | Notes |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]

    for index, score in enumerate(result.scores, start=1):
        status = "pass" if score.hard_filter.passed else "filtered"
        reasons = (
            "; ".join(score.hard_filter.reasons) if score.hard_filter.reasons else score.explanation
        )
        lines.append(
            "| "
            f"{index} | {score.candidate.name} | {status} | {score.total_score:.2f} | "
            f"{score.weather_score:.2f} | {score.evidence_quality_score:.2f} | {reasons} |"
        )

    lines.extend(["", "## Evidence", ""])

    for score in result.scores:
        lines.append(f"### {score.candidate.name}")
        for evidence in score.evidence:
            valid_until = evidence.valid_until.isoformat() if evidence.valid_until else "unknown"
            lines.extend(
                [
                    "",
                    f"- Source: {evidence.source_name}",
                    f"- Access: {evidence.access_method.value}",
                    f"- Collected at: {evidence.collected_at.isoformat()}",
                    f"- Valid until: {valid_until}",
                    f"- Reference: {evidence.url_or_reference}",
                ]
            )
        lines.append("")

    lines.extend(
        [
            "## Caveats",
            "",
            "- This spike only evaluates weather. Transport, cost, visa, POI, food, "
            "and social inspiration are not included yet.",
            "- Forecasts should be refreshed before booking or departure.",
        ]
    )
    return "\n".join(lines).strip() + "\n"
