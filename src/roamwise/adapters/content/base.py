from __future__ import annotations

from typing import Protocol

from roamwise.core.models import ContentResearchQuery, ContentResearchResult


class ContentResearchAdapter(Protocol):
    """Adapter contract for social, guide, and inspiration sources."""

    async def research(self, query: ContentResearchQuery) -> ContentResearchResult:
        """Return structured destination mentions and evidence for an agent to inspect."""
