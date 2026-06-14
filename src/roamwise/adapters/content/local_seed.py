from __future__ import annotations

from datetime import UTC, datetime, timedelta

from roamwise.core.models import (
    AccessMethod,
    ContentMention,
    ContentResearchQuery,
    ContentResearchResult,
    Evidence,
    SourceType,
)


class LocalContentSeedAdapter:
    """Local inspiration seed adapter.

    This adapter is a scaffold for the content-research contract. It is not a
    production recommendation source. Replace or augment it with approved
    Xiaohongshu, Zhihu, Trip.com, search, MCP, or OpenCLI adapters.
    """

    async def research(self, query: ContentResearchQuery) -> ContentResearchResult:
        mentions = [
            _normalize_local_seed_mention(mention)
            for mention in _LOCAL_MENTIONS
            if _matches_query(mention, query)
        ][: query.limit]
        collected_at = datetime.now(UTC)
        evidence = Evidence(
            source_name="LocalContentSeed",
            source_type=SourceType.INSPIRATION,
            access_method=AccessMethod.MANUAL,
            query=query.model_dump(mode="json"),
            url_or_reference="local://content-seeds",
            collected_at=collected_at,
            valid_until=collected_at + timedelta(days=30),
            fact_type="content.inspiration.seed",
            fact_value={"mentions": [mention.model_dump(mode="json") for mention in mentions]},
            confidence=0.35,
            is_factual=False,
            needs_corroboration=True,
        )
        return ContentResearchResult(query=query, mentions=mentions, evidence=[evidence])


def _matches_query(mention: ContentMention, query: ContentResearchQuery) -> bool:
    if query.destination_names and mention.destination_name not in query.destination_names:
        return False

    haystack = " ".join(
        [
            mention.destination_name,
            mention.title,
            mention.summary,
            " ".join(mention.themes),
            " ".join(mention.itinerary_patterns),
        ]
    ).lower()
    query_tokens = [token.lower() for token in query.query.split() if token.strip()]
    theme_tokens = [theme.lower() for theme in query.themes]
    tokens = query_tokens + theme_tokens
    return not tokens or any(token in haystack for token in tokens)


def _normalize_local_seed_mention(mention: ContentMention) -> ContentMention:
    return mention.model_copy(
        update={
            "platform_hint": "local_seed",
            "verification_needed": [
                "Replace or corroborate this local seed with live sources before relying on it."
            ],
            "risk_notes": [
                "Local seed data is a bootstrap example, not a production content source."
            ],
        }
    )


_LOCAL_MENTIONS = [
    ContentMention(
        destination_name="杭州",
        source_name="LocalContentSeed",
        access_method=AccessMethod.MANUAL,
        title="杭州三天公共交通玩法",
        url_or_reference="local://content-seeds/hangzhou-transit",
        summary="适合从上海出发，不自驾也能覆盖西湖、龙井、运河和市区美食。",
        themes=["西湖", "美食", "公共交通", "城市短途"],
        itinerary_patterns=["西湖半日步行", "龙井茶村", "运河夜游"],
        warnings=["雨天西湖步行体验下降", "热门餐厅需要排队"],
        confidence=0.45,
    ),
    ContentMention(
        destination_name="苏州",
        source_name="LocalContentSeed",
        access_method=AccessMethod.MANUAL,
        title="苏州园林和古城周末线",
        url_or_reference="local://content-seeds/suzhou-gardens",
        summary="高铁便利，但园林和古城区域节假日拥挤，适合文化和轻松城市游。",
        themes=["园林", "古城", "高铁", "文化"],
        itinerary_patterns=["拙政园", "平江路", "山塘街夜景"],
        warnings=["热门园林需要预约", "古城打车不如步行和地铁稳定"],
        confidence=0.45,
    ),
    ContentMention(
        destination_name="南京",
        source_name="LocalContentSeed",
        access_method=AccessMethod.MANUAL,
        title="南京博物馆历史路线",
        url_or_reference="local://content-seeds/nanjing-history",
        summary="适合历史、博物馆和美食主题，公共交通覆盖强，但夏季体感偏热。",
        themes=["历史", "博物馆", "美食", "公共交通"],
        itinerary_patterns=["南京博物院", "总统府", "秦淮河夜游"],
        warnings=["热门博物馆需预约", "高温天气需要减少户外暴走"],
        confidence=0.45,
    ),
    ContentMention(
        destination_name="宁波",
        source_name="LocalContentSeed",
        access_method=AccessMethod.MANUAL,
        title="宁波海鲜和城市短途",
        url_or_reference="local://content-seeds/ningbo-food",
        summary="海鲜和城市休闲较突出，不自驾可玩市区，远郊海岛需要额外交通确认。",
        themes=["海鲜", "城市", "美食", "短途"],
        itinerary_patterns=["天一阁", "老外滩", "海鲜餐厅"],
        warnings=["海岛和远郊不适合只依赖市内公共交通"],
        confidence=0.42,
    ),
]
