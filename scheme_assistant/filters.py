"""
filters.py — SchemeFilter: keyword search and category / state filtering.
"""

from __future__ import annotations

from .models import Scheme


class SchemeFilter:
    """
    Collection of pure filter functions that operate on a list of schemes.

    Each method returns a new list and does not mutate its input.
    """

    def by_keyword(self, schemes: list[Scheme], keyword: str) -> list[Scheme]:
        """
        Return schemes whose name, description, or tags contain *keyword*.

        The match is case-insensitive and partial (substring).

        Parameters
        ----------
        schemes:
            The list of schemes to search through.
        keyword:
            The search term. Leading/trailing whitespace is stripped.

        Returns
        -------
        list[Scheme]
            All schemes that contain the keyword in name, description, or tags.
        """
        kw = keyword.strip().lower()
        if not kw:
            return []

        result: list[Scheme] = []
        for scheme in schemes:
            haystack = (
                scheme.name.lower()
                + " "
                + scheme.description.lower()
                + " "
                + " ".join(scheme.tags)
            )
            if kw in haystack:
                result.append(scheme)
        return result

    def by_scheme_category(
        self, schemes: list[Scheme], category: str
    ) -> list[Scheme]:
        """
        Return schemes belonging to *category*.

        Pass ``"All"`` (or an empty string) to return all schemes unchanged.

        Parameters
        ----------
        schemes:
            The list of schemes to filter.
        category:
            A scheme category string such as ``"Agriculture"`` or ``"Education"``.
            Use ``"All"`` for no filtering.
        """
        if not category or category.strip().lower() == "all":
            return list(schemes)
        return [s for s in schemes if s.scheme_category == category]

    def by_state(self, schemes: list[Scheme], state: str) -> list[Scheme]:
        """
        Return National schemes plus state-specific schemes matching *state*.

        Parameters
        ----------
        schemes:
            The list of schemes to filter.
        state:
            A state name such as ``"Maharashtra"``.
            Use ``"All"`` (or an empty string) to return all schemes.
        """
        if not state or state.strip().lower() == "all":
            return list(schemes)
        return [
            s for s in schemes if s.state == "National" or s.state == state
        ]
