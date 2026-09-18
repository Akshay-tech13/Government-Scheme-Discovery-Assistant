"""
tests/test_eligibility.py — Unit tests for EligibilityChecker.
"""

from __future__ import annotations

import pytest

from scheme_assistant.eligibility import EligibilityChecker
from scheme_assistant.models import Scheme, UserProfile


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


def _make_scheme(**overrides) -> Scheme:
    """Create a permissive base scheme; override only what the test needs."""
    defaults = dict(
        id="SCH_001",
        name="Test Scheme",
        description="A test scheme",
        benefits="Some benefit",
        department="Test Dept",
        scheme_category="General",
        state="National",
        min_age=18,
        max_age=60,
        max_income=200_000.0,
        eligible_genders=["All"],
        eligible_categories=["All"],
        eligible_occupations=["All"],
        tags=[],
    )
    defaults.update(overrides)
    return Scheme(**defaults)


def _make_profile(**overrides) -> UserProfile:
    """Create a standard passing profile; override only what the test needs."""
    defaults = dict(
        age=30,
        annual_income=100_000.0,
        state="Maharashtra",
        category="General",
        occupation="Farmer",
        gender="Male",
    )
    defaults.update(overrides)
    return UserProfile(**defaults)


checker = EligibilityChecker()


# ---------------------------------------------------------------------------
# Age checks
# ---------------------------------------------------------------------------


class TestAgeEligibility:
    def test_age_within_range_passes(self):
        scheme = _make_scheme(min_age=18, max_age=60)
        assert checker.check_one(_make_profile(age=30), scheme) is True

    def test_age_at_min_boundary_passes(self):
        scheme = _make_scheme(min_age=18, max_age=60)
        assert checker.check_one(_make_profile(age=18), scheme) is True

    def test_age_at_max_boundary_passes(self):
        scheme = _make_scheme(min_age=18, max_age=60)
        assert checker.check_one(_make_profile(age=60), scheme) is True

    def test_age_below_min_fails(self):
        scheme = _make_scheme(min_age=18, max_age=60)
        assert checker.check_one(_make_profile(age=17), scheme) is False

    def test_age_above_max_fails(self):
        scheme = _make_scheme(min_age=18, max_age=60)
        assert checker.check_one(_make_profile(age=61), scheme) is False


# ---------------------------------------------------------------------------
# Income checks
# ---------------------------------------------------------------------------


class TestIncomeEligibility:
    def test_income_below_ceiling_passes(self):
        scheme = _make_scheme(max_income=200_000.0)
        assert checker.check_one(_make_profile(annual_income=100_000.0), scheme) is True

    def test_income_equal_to_ceiling_passes(self):
        scheme = _make_scheme(max_income=200_000.0)
        assert checker.check_one(_make_profile(annual_income=200_000.0), scheme) is True

    def test_income_above_ceiling_fails(self):
        scheme = _make_scheme(max_income=200_000.0)
        assert checker.check_one(_make_profile(annual_income=200_001.0), scheme) is False

    def test_no_income_limit_passes(self):
        scheme = _make_scheme(max_income=9_999_999.0)
        assert checker.check_one(_make_profile(annual_income=5_000_000.0), scheme) is True


# ---------------------------------------------------------------------------
# State checks
# ---------------------------------------------------------------------------


class TestStateEligibility:
    def test_national_scheme_passes_any_state(self):
        scheme = _make_scheme(state="National")
        assert checker.check_one(_make_profile(state="Rajasthan"), scheme) is True

    def test_state_specific_scheme_passes_matching_state(self):
        scheme = _make_scheme(state="Maharashtra")
        assert checker.check_one(_make_profile(state="Maharashtra"), scheme) is True

    def test_state_specific_scheme_fails_different_state(self):
        scheme = _make_scheme(state="Maharashtra")
        assert checker.check_one(_make_profile(state="Rajasthan"), scheme) is False


# ---------------------------------------------------------------------------
# Social category checks
# ---------------------------------------------------------------------------


class TestCategoryEligibility:
    def test_all_category_passes_any_user_category(self):
        scheme = _make_scheme(eligible_categories=["All"])
        assert checker.check_one(_make_profile(category="SC"), scheme) is True

    def test_specific_category_passes_matching(self):
        scheme = _make_scheme(eligible_categories=["SC", "ST"])
        assert checker.check_one(_make_profile(category="SC"), scheme) is True

    def test_specific_category_fails_non_matching(self):
        scheme = _make_scheme(eligible_categories=["SC", "ST"])
        assert checker.check_one(_make_profile(category="General"), scheme) is False


# ---------------------------------------------------------------------------
# Gender checks
# ---------------------------------------------------------------------------


class TestGenderEligibility:
    def test_all_gender_passes_any_user_gender(self):
        scheme = _make_scheme(eligible_genders=["All"])
        assert checker.check_one(_make_profile(gender="Male"), scheme) is True

    def test_female_only_scheme_passes_for_female(self):
        scheme = _make_scheme(eligible_genders=["Female"])
        assert checker.check_one(_make_profile(gender="Female"), scheme) is True

    def test_female_only_scheme_fails_for_male(self):
        scheme = _make_scheme(eligible_genders=["Female"])
        assert checker.check_one(_make_profile(gender="Male"), scheme) is False


# ---------------------------------------------------------------------------
# Occupation checks
# ---------------------------------------------------------------------------


class TestOccupationEligibility:
    def test_all_occupation_passes_any_user_occupation(self):
        scheme = _make_scheme(eligible_occupations=["All"])
        assert checker.check_one(_make_profile(occupation="Student"), scheme) is True

    def test_specific_occupation_passes_matching(self):
        scheme = _make_scheme(eligible_occupations=["Farmer"])
        assert checker.check_one(_make_profile(occupation="Farmer"), scheme) is True

    def test_specific_occupation_fails_non_matching(self):
        scheme = _make_scheme(eligible_occupations=["Farmer"])
        assert checker.check_one(_make_profile(occupation="Student"), scheme) is False


# ---------------------------------------------------------------------------
# Combined AND logic
# ---------------------------------------------------------------------------


class TestCombinedEligibility:
    def test_all_criteria_met_returns_true(self):
        scheme = _make_scheme(
            min_age=18, max_age=60,
            max_income=200_000.0,
            state="National",
            eligible_genders=["Female"],
            eligible_categories=["SC"],
            eligible_occupations=["Student"],
        )
        profile = _make_profile(
            age=25, annual_income=100_000.0, state="Maharashtra",
            gender="Female", category="SC", occupation="Student",
        )
        assert checker.check_one(profile, scheme) is True

    def test_one_criterion_fails_returns_false(self):
        scheme = _make_scheme(eligible_occupations=["Farmer"])
        profile = _make_profile(occupation="Student")  # Wrong occupation
        assert checker.check_one(profile, scheme) is False

    def test_get_eligible_returns_only_matching_schemes(self):
        farmer_scheme = _make_scheme(id="F1", eligible_occupations=["Farmer"])
        student_scheme = _make_scheme(id="S1", eligible_occupations=["Student"])
        open_scheme = _make_scheme(id="O1", eligible_occupations=["All"])

        farmer_profile = _make_profile(occupation="Farmer")
        results = checker.get_eligible(farmer_profile, [farmer_scheme, student_scheme, open_scheme])
        result_ids = {s.id for s in results}
        assert "F1" in result_ids
        assert "O1" in result_ids
        assert "S1" not in result_ids

    def test_get_eligible_returns_empty_when_no_match(self):
        scheme = _make_scheme(max_income=10_000.0)
        profile = _make_profile(annual_income=500_000.0)
        assert checker.get_eligible(profile, [scheme]) == []

    def test_get_eligible_empty_scheme_list(self):
        assert checker.get_eligible(_make_profile(), []) == []
