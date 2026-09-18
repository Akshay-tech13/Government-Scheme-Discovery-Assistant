"""
tests/test_models.py — Unit tests for UserProfile and Scheme dataclasses.
"""

import pytest

from scheme_assistant.models import Scheme, UserProfile


# ---------------------------------------------------------------------------
# UserProfile validation
# ---------------------------------------------------------------------------


class TestUserProfile:
    def _valid_profile(self, **overrides) -> UserProfile:
        defaults = dict(
            age=30,
            annual_income=150_000.0,
            state="Maharashtra",
            category="OBC",
            occupation="Farmer",
            gender="Male",
        )
        defaults.update(overrides)
        return UserProfile(**defaults)

    def test_valid_profile_creates_successfully(self):
        profile = self._valid_profile()
        assert profile.age == 30
        assert profile.annual_income == 150_000.0
        assert profile.state == "Maharashtra"

    def test_age_zero_raises(self):
        with pytest.raises(ValueError, match="Age must be between"):
            self._valid_profile(age=0)

    def test_age_negative_raises(self):
        with pytest.raises(ValueError, match="Age must be between"):
            self._valid_profile(age=-5)

    def test_age_above_120_raises(self):
        with pytest.raises(ValueError, match="Age must be between"):
            self._valid_profile(age=121)

    def test_age_boundary_low(self):
        profile = self._valid_profile(age=1)
        assert profile.age == 1

    def test_age_boundary_high(self):
        profile = self._valid_profile(age=120)
        assert profile.age == 120

    def test_negative_income_raises(self):
        with pytest.raises(ValueError, match="Annual income cannot be negative"):
            self._valid_profile(annual_income=-1.0)

    def test_zero_income_is_valid(self):
        profile = self._valid_profile(annual_income=0.0)
        assert profile.annual_income == 0.0

    def test_empty_state_raises(self):
        with pytest.raises(ValueError, match="state"):
            self._valid_profile(state="")

    def test_whitespace_state_raises(self):
        with pytest.raises(ValueError, match="state"):
            self._valid_profile(state="   ")

    def test_empty_category_raises(self):
        with pytest.raises(ValueError, match="category"):
            self._valid_profile(category="")

    def test_empty_occupation_raises(self):
        with pytest.raises(ValueError, match="occupation"):
            self._valid_profile(occupation="")

    def test_empty_gender_raises(self):
        with pytest.raises(ValueError, match="gender"):
            self._valid_profile(gender="")


# ---------------------------------------------------------------------------
# Scheme.short_description
# ---------------------------------------------------------------------------


class TestSchemeShortDescription:
    def _make_scheme(self, description: str) -> Scheme:
        return Scheme(
            id="TEST_001",
            name="Test Scheme",
            description=description,
            benefits="Some benefit",
            department="Test Dept",
            scheme_category="Education",
            state="National",
            min_age=18,
            max_age=60,
            max_income=200_000.0,
            eligible_genders=["All"],
            eligible_categories=["All"],
            eligible_occupations=["All"],
            tags=[],
        )

    def test_short_description_unchanged_when_within_limit(self):
        scheme = self._make_scheme("Short desc")
        assert scheme.short_description() == "Short desc"

    def test_short_description_truncated_when_over_limit(self):
        long_text = "A" * 200
        result = self._make_scheme(long_text).short_description(max_chars=50)
        assert len(result) <= 53  # 50 chars + "…"
        assert result.endswith("…")

    def test_short_description_exact_limit_not_truncated(self):
        text = "B" * 120
        scheme = self._make_scheme(text)
        result = scheme.short_description()
        assert result == text
        assert not result.endswith("…")
