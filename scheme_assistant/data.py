"""
data.py — SchemeRepository: loads and provides access to scheme data from schemes.json.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from .exceptions import SchemeNotFoundError
from .models import Scheme


_DEFAULT_JSON_PATH = Path(__file__).parent / "schemes.json"


class SchemeRepository:
    """
    Loads schemes from a JSON file and provides read access.

    Parameters
    ----------
    json_path:
        Path to the JSON file containing scheme records.
        Defaults to the bundled ``schemes.json``.
    """

    def __init__(self, json_path: Path | str | None = None) -> None:
        self._path = Path(json_path) if json_path else _DEFAULT_JSON_PATH
        self._schemes: list[Scheme] = []
        self._load()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Read and parse the JSON file into Scheme objects."""
        if not self._path.exists():
            raise FileNotFoundError(f"Scheme data file not found: {self._path}")

        with open(self._path, encoding="utf-8") as fh:
            raw: list[dict] = json.load(fh)

        seen_ids: set[str] = set()
        for record in raw:
            scheme_id = record.get("id", "")
            if scheme_id in seen_ids:
                # Skip duplicates silently (log-friendly message)
                print(f"[WARNING] Duplicate scheme id '{scheme_id}' — skipped.")
                continue
            seen_ids.add(scheme_id)
            self._schemes.append(self._from_dict(record))

    @staticmethod
    def _from_dict(d: dict) -> Scheme:
        """Convert a raw dictionary to a Scheme dataclass instance."""
        return Scheme(
            id=d["id"],
            name=d["name"],
            description=d["description"],
            benefits=d["benefits"],
            department=d["department"],
            scheme_category=d["scheme_category"],
            state=d["state"],
            min_age=int(d["min_age"]),
            max_age=int(d["max_age"]),
            max_income=float(d["max_income"]),
            eligible_genders=list(d.get("eligible_genders", ["All"])),
            eligible_categories=list(d.get("eligible_categories", ["All"])),
            eligible_occupations=list(d.get("eligible_occupations", ["All"])),
            tags=list(d.get("tags", [])),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_all(self) -> list[Scheme]:
        """Return a copy of the full scheme list."""
        return list(self._schemes)

    def get_by_id(self, scheme_id: str) -> Scheme:
        """
        Return the scheme matching *scheme_id*.

        Raises
        ------
        SchemeNotFoundError
            If no scheme with the given ID exists.
        """
        for scheme in self._schemes:
            if scheme.id == scheme_id:
                return scheme
        raise SchemeNotFoundError(scheme_id)

    def all_scheme_categories(self) -> list[str]:
        """Return a sorted deduplicated list of all scheme categories."""
        return sorted({s.scheme_category for s in self._schemes})

    def all_states(self) -> list[str]:
        """Return a sorted deduplicated list of all states (including National)."""
        return sorted({s.state for s in self._schemes})
