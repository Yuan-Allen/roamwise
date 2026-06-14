from __future__ import annotations

import pytest

from roamwise.adapters.content import LocalContentSeedAdapter
from roamwise.core.content import candidate_names_from_mentions
from roamwise.core.models import ContentResearchQuery


@pytest.mark.asyncio
async def test_local_content_seed_returns_structured_mentions() -> None:
    adapter = LocalContentSeedAdapter()

    result = await adapter.research(
        ContentResearchQuery(query="公共交通 美食", origin="上海", limit=3)
    )

    assert result.mentions
    assert result.mentions[0].evidence_role == "inspiration"
    assert result.mentions[0].source_freshness == "unknown"
    assert result.evidence[0].needs_corroboration is True
    assert "杭州" in candidate_names_from_mentions(result)


@pytest.mark.asyncio
async def test_local_content_seed_can_filter_destinations() -> None:
    adapter = LocalContentSeedAdapter()

    result = await adapter.research(
        ContentResearchQuery(
            query="历史",
            origin="上海",
            destination_names=["南京"],
            limit=5,
        )
    )

    assert [mention.destination_name for mention in result.mentions] == ["南京"]
