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
    assert result.mentions[0].platform_hint == "public_web"
    assert result.mentions[0].evidence_role == "inspiration"
    assert result.mentions[0].verification_needed
    assert result.mentions[0].risk_notes
    assert result.evidence[0].source_name == "Tavily"
    assert result.evidence[0].needs_corroboration is True


@pytest.mark.asyncio
async def test_search_content_adapter_classifies_platform_roles() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "title": "杭州小红书周末攻略",
                        "url": "https://www.xiaohongshu.com/explore/1",
                        "content": "杭州 citywalk 好拍，也有人提醒雨天体验下降。",
                    },
                    {
                        "title": "杭州西湖景区官方公告",
                        "url": "https://westlake.hangzhou.gov.cn/notice",
                        "content": "杭州西湖景区发布预约和开放公告。",
                    },
                    {
                        "title": "杭州景点门票 - 携程",
                        "url": "https://you.ctrip.com/sight/hangzhou14.html",
                        "content": "携程提供杭州景点、门票和酒店区域参考。",
                    },
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
                query="杭州 周末 不自驾 美食",
                origin="上海",
                destination_names=["杭州"],
                themes=["美食", "公共交通"],
                limit=3,
            )
        )

    xhs, official, ctrip = result.mentions
    assert xhs.platform_hint == "xiaohongshu"
    assert xhs.source_type == "inspiration"
    assert xhs.evidence_role == "inspiration"
    assert xhs.verification_needed == [
        "Corroborate operational claims with official, map, weather, or transport sources."
    ]

    assert official.platform_hint == "official"
    assert official.source_type == "official"
    assert official.evidence_role == "factual_candidate"
    assert official.confidence > xhs.confidence

    assert ctrip.platform_hint == "ctrip"
    assert ctrip.source_type == "context"
    assert ctrip.evidence_role == "verification_needed"
    assert "booking" in ctrip.verification_needed[0].lower()


@pytest.mark.asyncio
async def test_search_content_adapter_requires_key() -> None:
    adapter = SearchContentAdapter(api_key="")

    with pytest.raises(MissingSearchApiKeyError):
        await adapter.research(ContentResearchQuery(query="杭州攻略"))
