"""
eligibility.py — EligibilityChecker: pure logic, no Streamlit dependency.
"""

from __future__ import annotations

from .models import Scheme, UserProfile


class EligibilityChecker:
    """
    Checks whether a :class:`UserProfile` qualifies for a :class:`Scheme`.

    All criteria are AND-combined: the user must satisfy every rule.
    """

    def check_one(self, profile: UserProfile, scheme: Scheme) -> bool:
        """
        Return ``True`` if *profile* meets all eligibility criteria of *scheme*.

        Criteria checked (in order):
        1. Age is within [min_age, max_age].
        2. Annual income is within the scheme's max_income ceiling.
        3. State matches (or scheme is National).
        4. Social category matches (or scheme is open to All).
        5. Gender matches (or scheme is open to All).
        6. Occupation matches (or scheme is open to All).
        """
        # 1. Age range
        if not (scheme.min_age <= profile.age <= scheme.max_age):
            return False

        # 2. Income ceiling
        if profile.annual_income > scheme.max_income:
            return False

        # 3. State — "National" schemes are open to everyone
        if scheme.state != "National" and scheme.state != profile.state:
            return False

        # 4. Social category
        if "All" not in scheme.eligible_categories:
            if profile.category not in scheme.eligible_categories:
                return False

        # 5. Gender
        if "All" not in scheme.eligible_genders:
            if profile.gender not in scheme.eligible_genders:
                return False

        # 6. Occupation
        if "All" not in scheme.eligible_occupations:
            if profile.occupation not in scheme.eligible_occupations:
                return False

        return True

    def get_eligible(
        self, profile: UserProfile, schemes: list[Scheme]
    ) -> list[Scheme]:
        """
        Return the subset of *schemes* for which *profile* is eligible.

        Parameters
        ----------
        profile:
            The citizen's personal details.
        schemes:
            The full list of schemes to evaluate.

        Returns
        -------
        list[Scheme]
            Possibly empty list of matching schemes.
        """
        return [s for s in schemes if self.check_one(profile, s)]
