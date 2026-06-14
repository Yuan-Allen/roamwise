from __future__ import annotations

import httpx
import pytest

from roamwise.adapters.content import MissingSearchApiKeyError, SearchContentAdapter
from roamwise.core.models import ContentResearchQuery


@pytest.mark.asyncio
async def test_search_content_adapter_normalizes_results() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/search"
        payload = request.read().decode("utf-8")
        assert "杭州" in payload
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "title": "杭州三日游攻略 - 公开网页",
                        "url": "https://example.test/hangzhou",
                        "content": "杭州适合公共交通旅行，西湖和运河路线较成熟。",
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        adapter = SearchContentAdapter(
            api_key="test-key",
            http_client=http_client,
            endpoint="https://example.test/search",
        )
        result = await adapter.research(
            ContentResearchQuery(
                query="公共交通 旅行攻略",
                origin="上海",
                destination_names=["杭州", "苏州"],
                themes=["公共交通"],
                limit=3,
            )
        )

    assert result.mentions[0].destination_name == "杭州"
    assert result.mentions[0].access_method == "search"
    assert result.evidence[0].source_name == "Tavily"
    assert result.evidence[0].needs_corroboration is True


@pytest.mark.asyncio
async def test_search_content_adapter_requires_key() -> None:
    adapter = SearchContentAdapter(api_key="")

    with pytest.raises(MissingSearchApiKeyError):
        await adapter.research(ContentResearchQuery(query="杭州攻略"))
