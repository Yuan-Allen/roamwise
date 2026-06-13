from __future__ import annotations

from roamwise.core.candidates import ensure_candidates, generate_candidates
from roamwise.core.models import DateRange, TravelRequest


def test_generate_candidates_ranks_nearby_shanghai_options() -> None:
    candidates = generate_candidates("上海", limit=3)

    assert [candidate.name for candidate in candidates] == ["苏州", "无锡", "宁波"]


def test_ensure_candidates_keeps_explicit_candidates() -> None:
    request = TravelRequest(
        origin="上海",
        date_range=DateRange(start="2026-06-24", end="2026-06-26"),
        candidates=[generate_candidates("上海", limit=1)[0]],
    )

    updated = ensure_candidates(request)

    assert updated.candidates == request.candidates


def test_ensure_candidates_adds_defaults_when_missing() -> None:
    request = TravelRequest(
        origin="上海",
        date_range=DateRange(start="2026-06-24", end="2026-06-26"),
    )

    updated = ensure_candidates(request, limit=2)

    assert len(updated.candidates) == 2
    assert request.candidates == []
