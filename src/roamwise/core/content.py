from __future__ import annotations

from roamwise.core.models import ContentMention, ContentResearchResult, DestinationCandidate


def candidate_names_from_mentions(result: ContentResearchResult) -> list[str]:
    names: list[str] = []
    for mention in result.mentions:
        if mention.destination_name not in names:
            names.append(mention.destination_name)
    return names


def mentions_for_candidate(
    result: ContentResearchResult,
    candidate: DestinationCandidate,
) -> list[ContentMention]:
    return [mention for mention in result.mentions if mention.destination_name == candidate.name]
