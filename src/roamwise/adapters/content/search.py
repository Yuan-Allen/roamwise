from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from roamwise.core.models import (
    AccessMethod,
    ContentAccessPolicy,
    ContentEvidenceRole,
    ContentMention,
    ContentResearchQuery,
    ContentResearchResult,
    Evidence,
    SourceFreshness,
    SourceType,
)
from roamwise.core.settings import Settings

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


class MissingSearchApiKeyError(RuntimeError):
    """Raised when a search provider key is not configured."""


class SearchContentAdapter:
    """Low-risk public web search adapter for content discovery.

    This adapter should be used before higher-risk browser/OpenCLI platform access.
    It returns public source references for the agent to inspect and synthesize.
    """

    def __init__(
        self,
        api_key: str | None = None,
        http_client: httpx.AsyncClient | None = None,
        endpoint: str = TAVILY_SEARCH_URL,
        policy: ContentAccessPolicy | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else Settings().tavily_api_key
        self._client = http_client
        self._endpoint = endpoint
        self._policy = policy or ContentAccessPolicy(min_delay_seconds=0)

    async def research(self, query: ContentResearchQuery) -> ContentResearchResult:
        if not self._api_key:
            raise MissingSearchApiKeyError("TAVILY_API_KEY is required for SearchContentAdapter")

        limited_query = query.model_copy(
            update={"limit": min(query.limit, self._policy.max_items_per_query)}
        )
        payload = await self._search(limited_query)
        mentions = _mentions_from_tavily(limited_query, payload)
        collected_at = datetime.now(UTC)
        evidence = Evidence(
            source_name="Tavily",
            source_type=SourceType.INSPIRATION,
            access_method=AccessMethod.SEARCH,
            query=limited_query.model_dump(mode="json"),
            url_or_reference=self._endpoint,
            collected_at=collected_at,
            valid_until=collected_at + timedelta(hours=self._policy.cache_ttl_hours),
            fact_type="content.search.results",
            fact_value=payload,
            confidence=0.55,
            is_factual=False,
            needs_corroboration=True,
        )
        return ContentResearchResult(query=limited_query, mentions=mentions, evidence=[evidence])

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError)),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _search(self, query: ContentResearchQuery) -> dict[str, Any]:
        request_payload = {
            "api_key": self._api_key,
            "query": _build_search_query(query),
            "max_results": query.limit,
            "search_depth": "basic",
            "include_answer": False,
            "include_raw_content": False,
        }
        if self._client is not None:
            response = await self._client.post(self._endpoint, json=request_payload)
            response.raise_for_status()
            return response.json()

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(self._endpoint, json=request_payload)
            response.raise_for_status()
            return response.json()


def _build_search_query(query: ContentResearchQuery) -> str:
    parts = [query.query]
    if query.origin:
        parts.append(f"从{query.origin}出发")
    if query.destination_names:
        parts.append(" ".join(query.destination_names))
    if query.themes:
        parts.append(" ".join(query.themes))
    return " ".join(part for part in parts if part).strip()


def _mentions_from_tavily(
    query: ContentResearchQuery,
    payload: dict[str, Any],
) -> list[ContentMention]:
    results = payload.get("results") or []
    mentions: list[ContentMention] = []
    for item in results[: query.limit]:
        title = item.get("title") or "Untitled search result"
        url = item.get("url") or "search://unknown"
        content = item.get("content") or item.get("snippet") or ""
        destination = _infer_destination(query.destination_names, f"{title} {content}")
        if destination is None:
            destination = query.destination_names[0] if query.destination_names else "unknown"
        platform_hint = _infer_platform_hint(url, f"{title} {content}")
        source_type = _source_type_for_platform(platform_hint)
        evidence_role = _evidence_role_for_platform(platform_hint)
        verification_needed = _verification_needed_for_platform(platform_hint)
        risk_notes = _risk_notes_for_platform(platform_hint)
        mentions.append(
            ContentMention(
                destination_name=destination,
                source_name=_source_name_for_platform(platform_hint),
                source_type=source_type,
                access_method=AccessMethod.SEARCH,
                platform_hint=platform_hint,
                evidence_role=evidence_role,
                title=title,
                url_or_reference=url,
                summary=content[:500],
                themes=[theme for theme in query.themes if theme in f"{title} {content}"],
                candidate_expansion=_candidate_expansion(query.destination_names, destination),
                verification_needed=verification_needed,
                source_freshness=SourceFreshness.UNKNOWN,
                risk_notes=risk_notes,
                itinerary_patterns=[],
                warnings=_warnings_for_platform(platform_hint),
                confidence=_confidence_for_platform(platform_hint),
            )
        )
    return mentions


def _infer_destination(destination_names: list[str], text: str) -> str | None:
    for name in destination_names:
        if name in text:
            return name
    return None


def _infer_platform_hint(url: str, text: str) -> str:
    normalized = f"{url} {text}".lower()
    if "xiaohongshu.com" in normalized or "xhslink.com" in normalized or "小红书" in text:
        return "xiaohongshu"
    if "zhihu.com" in normalized or "知乎" in text:
        return "zhihu"
    if "ctrip.com" in normalized or "携程" in text:
        return "ctrip"
    if "trip.com" in normalized or "trip.com" in text.lower():
        return "trip.com"
    if "mafengwo.cn" in normalized or "马蜂窝" in text:
        return "mafengwo"
    if "tripadvisor." in normalized or "tripadvisor" in text.lower():
        return "tripadvisor"
    if "reddit.com" in normalized:
        return "reddit"
    if _looks_official(normalized):
        return "official"
    if "blog" in normalized or "forum" in normalized or "bbs" in normalized:
        return "blog_or_forum"
    return "public_web"


def _looks_official(normalized: str) -> bool:
    official_markers = [
        ".gov",
        "gov.cn",
        "gouv.",
        "go.jp",
        "tourism",
        "travel.state.gov",
        "mfa.gov",
        "embassy",
        "museum",
        "park",
        "airport",
        "railway",
    ]
    return any(marker in normalized for marker in official_markers)


def _source_type_for_platform(platform_hint: str) -> SourceType:
    if platform_hint == "official":
        return SourceType.OFFICIAL
    if platform_hint in {"ctrip", "trip.com", "tripadvisor"}:
        return SourceType.CONTEXT
    return SourceType.INSPIRATION


def _evidence_role_for_platform(platform_hint: str) -> ContentEvidenceRole:
    if platform_hint == "official":
        return ContentEvidenceRole.FACTUAL_CANDIDATE
    if platform_hint in {"ctrip", "trip.com", "tripadvisor"}:
        return ContentEvidenceRole.VERIFICATION_NEEDED
    return ContentEvidenceRole.INSPIRATION


def _source_name_for_platform(platform_hint: str) -> str:
    names = {
        "xiaohongshu": "Xiaohongshu",
        "zhihu": "Zhihu",
        "ctrip": "Ctrip",
        "trip.com": "Trip.com",
        "mafengwo": "Mafengwo",
        "tripadvisor": "Tripadvisor",
        "reddit": "Reddit",
        "official": "OfficialSource",
        "blog_or_forum": "BlogOrForum",
        "public_web": "PublicWeb",
    }
    return names.get(platform_hint, "PublicWeb")


def _verification_needed_for_platform(platform_hint: str) -> list[str]:
    if platform_hint == "official":
        return ["Inspect the official page and timestamp before relying on operational details."]
    if platform_hint in {"ctrip", "trip.com"}:
        return ["Verify live prices, tickets, availability, and booking rules before booking."]
    if platform_hint == "tripadvisor":
        return [
            "Cross-check ratings, opening status, and recent reviews "
            "against official or map sources."
        ]
    if platform_hint in {"xiaohongshu", "zhihu", "mafengwo", "reddit", "blog_or_forum"}:
        return ["Corroborate operational claims with official, map, weather, or transport sources."]
    return ["Inspect source page before using this search result as evidence."]


def _risk_notes_for_platform(platform_hint: str) -> list[str]:
    if platform_hint in {"xiaohongshu", "zhihu", "mafengwo", "reddit", "blog_or_forum"}:
        return [
            "Social or guide content is inspiration and may be subjective, stale, or incomplete."
        ]
    if platform_hint in {"ctrip", "trip.com"}:
        return [
            "Travel-commerce content can include availability or price hints that change quickly."
        ]
    if platform_hint == "official":
        return ["Search snippets can omit context; inspect the official page directly."]
    return ["Public search rank does not imply recommendation quality."]


def _warnings_for_platform(platform_hint: str) -> list[str]:
    return [
        "Public search result; agent must inspect source before relying on it.",
        *_verification_needed_for_platform(platform_hint),
    ]


def _confidence_for_platform(platform_hint: str) -> float:
    if platform_hint == "official":
        return 0.65
    if platform_hint in {"ctrip", "trip.com", "tripadvisor"}:
        return 0.55
    return 0.45


def _candidate_expansion(destination_names: list[str], destination: str) -> list[str]:
    if destination == "unknown" or destination in destination_names:
        return []
    return [destination]
