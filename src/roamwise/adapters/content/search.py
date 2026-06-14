from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from roamwise.core.models import (
    AccessMethod,
    ContentAccessPolicy,
    ContentMention,
    ContentResearchQuery,
    ContentResearchResult,
    Evidence,
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
        mentions.append(
            ContentMention(
                destination_name=destination,
                source_name="Tavily",
                access_method=AccessMethod.SEARCH,
                title=title,
                url_or_reference=url,
                summary=content[:500],
                themes=[theme for theme in query.themes if theme in f"{title} {content}"],
                itinerary_patterns=[],
                warnings=["Public search result; agent must inspect source before relying on it."],
                confidence=0.5,
            )
        )
    return mentions


def _infer_destination(destination_names: list[str], text: str) -> str | None:
    for name in destination_names:
        if name in text:
            return name
    return None
