"""
tests/test_filters.py — Unit tests for SchemeFilter.
"""

from __future__ import annotations

import pytest

from scheme_assistant.filters import SchemeFilter
from scheme_assistant.models import Scheme


# ---------------------------------------------------------------------------
# Fixture helper
# ---------------------------------------------------------------------------


def _make_scheme(
    id: str = "SCH_001",
    name: str = "Test Scheme",
    description: str = "A basic description",
    scheme_category: str = "Education",
    state: str = "National",
    tags: list[str] | None = None,
) -> Scheme:
    return Scheme(
        id=id,
        name=name,
        description=description,
        benefits="Some benefit",
        department="Test Dept",
        scheme_category=scheme_category,
        state=state,
        min_age=18,
        max_age=60,
        max_income=200_000.0,
        eligible_genders=["All"],
        eligible_categories=["All"],
        eligible_occupations=["All"],
        tags=tags or [],
    )


sf = SchemeFilter()


# ---------------------------------------------------------------------------
# by_keyword
# ---------------------------------------------------------------------------


class TestByKeyword:
    def test_matches_name(self):
        schemes = [_make_scheme(name="Farmer Subsidy Scheme")]
        results = sf.by_keyword(schemes, "farmer")
        assert len(results) == 1

    def test_matches_description(self):
        schemes = [_make_scheme(description="This scheme is for student education")]
        results = sf.by_keyword(schemes, "education")
        assert len(results) == 1

    def test_matches_tags(self):
        schemes = [_make_scheme(tags=["loan", "women", "self-employed"])]
        results = sf.by_keyword(schemes, "loan")
        assert len(results) == 1

    def test_case_insensitive(self):
        schemes = [_make_scheme(name="Farmer Income Support")]
        results = sf.by_keyword(schemes, "FARMER")
        assert len(results) == 1

    def test_partial_match(self):
        schemes = [_make_scheme(description="agricultural subsidy programme")]
        results = sf.by_keyword(schemes, "agri")
        assert len(results) == 1

    def test_no_match_returns_empty(self):
        schemes = [_make_scheme(name="Health Scheme", description="hospital benefit")]
        results = sf.by_keyword(schemes, "farmer")
        assert results == []

    def test_empty_keyword_returns_empty(self):
        schemes = [_make_scheme()]
        assert sf.by_keyword(schemes, "") == []

    def test_whitespace_only_keyword_returns_empty(self):
        schemes = [_make_scheme()]
        assert sf.by_keyword(schemes, "   ") == []

    def test_multiple_matches(self):
        schemes = [
            _make_scheme(id="A", name="Agriculture Loan"),
            _make_scheme(id="B", name="Education Grant"),
            _make_scheme(id="C", description="For agricultural workers"),
        ]
        results = sf.by_keyword(schemes, "agri")
        ids = {s.id for s in results}
        assert "A" in ids
        assert "C" in ids
        assert "B" not in ids

    def test_empty_scheme_list_returns_empty(self):
        assert sf.by_keyword([], "farmer") == []


# ---------------------------------------------------------------------------
# by_scheme_category
# ---------------------------------------------------------------------------


class TestBySchemCategory:
    def _sample_schemes(self) -> list[Scheme]:
        return [
            _make_scheme(id="A", scheme_category="Education"),
            _make_scheme(id="B", scheme_category="Agriculture"),
            _make_scheme(id="C", scheme_category="Health"),
        ]

    def test_filters_to_matching_category(self):
        results = sf.by_scheme_category(self._sample_schemes(), "Education")
        assert len(results) == 1
        assert results[0].id == "A"

    def test_all_returns_all_schemes(self):
        results = sf.by_scheme_category(self._sample_schemes(), "All")
        assert len(results) == 3

    def test_empty_string_returns_all_schemes(self):
        results = sf.by_scheme_category(self._sample_schemes(), "")
        assert len(results) == 3

    def test_non_existent_category_returns_empty(self):
        results = sf.by_scheme_category(self._sample_schemes(), "Housing")
        assert results == []

    def test_empty_scheme_list(self):
        assert sf.by_scheme_category([], "Education") == []


# ---------------------------------------------------------------------------
# by_state
# ---------------------------------------------------------------------------


class TestByState:
    def _sample_schemes(self) -> list[Scheme]:
        return [
            _make_scheme(id="NAT1", state="National"),
            _make_scheme(id="NAT2", state="National"),
            _make_scheme(id="MH1", state="Maharashtra"),
            _make_scheme(id="RJ1", state="Rajasthan"),
        ]

    def test_returns_national_plus_matching_state(self):
        results = sf.by_state(self._sample_schemes(), "Maharashtra")
        ids = {s.id for s in results}
        assert "NAT1" in ids
        assert "NAT2" in ids
        assert "MH1" in ids
        assert "RJ1" not in ids

    def test_different_state_returns_national_only(self):
        results = sf.by_state(self._sample_schemes(), "Rajasthan")
        ids = {s.id for s in results}
        assert "NAT1" in ids
        assert "NAT2" in ids
        assert "RJ1" in ids
        assert "MH1" not in ids

    def test_all_returns_all_schemes(self):
        results = sf.by_state(self._sample_schemes(), "All")
        assert len(results) == 4

    def test_empty_string_returns_all(self):
        results = sf.by_state(self._sample_schemes(), "")
        assert len(results) == 4

    def test_state_with_no_specific_schemes_returns_national(self):
        results = sf.by_state(self._sample_schemes(), "Kerala")
        ids = {s.id for s in results}
        assert "NAT1" in ids
        assert "NAT2" in ids
        assert "MH1" not in ids
        assert "RJ1" not in ids

    def test_empty_scheme_list(self):
        assert sf.by_state([], "Maharashtra") == []
