"""
models.py — Data containers for the Government Scheme Discovery Assistant.

Uses Python dataclasses with type hints.  No business logic lives here.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UserProfile:
    """Represents the personal details entered by a citizen."""

    age: int
    annual_income: float
    state: str
    category: str        # General / SC / ST / OBC / EWS
    occupation: str      # Farmer / Student / Salaried / Self-employed / Unemployed / Other
    gender: str          # Male / Female / Other

    def __post_init__(self) -> None:
        if self.age < 1 or self.age > 120:
            raise ValueError(f"Age must be between 1 and 120, got {self.age}.")
        if self.annual_income < 0:
            raise ValueError(f"Annual income cannot be negative, got {self.annual_income}.")
        for field_name, value in [
            ("state", self.state),
            ("category", self.category),
            ("occupation", self.occupation),
            ("gender", self.gender),
        ]:
            if not value or not value.strip():
                raise ValueError(f"Field '{field_name}' must not be empty.")


@dataclass
class Scheme:
    """Represents a single government scheme."""

    id: str
    name: str
    description: str
    benefits: str
    department: str
    scheme_category: str          # Agriculture / Education / Health / Housing / Women / Other
    state: str                    # "National" or a specific state name
    min_age: int
    max_age: int
    max_income: float             # Use 9_999_999 to indicate no income ceiling
    eligible_genders: list[str]   # ["All"] or ["Female"] etc.
    eligible_categories: list[str]  # ["All"] or ["SC", "ST"] etc.
    eligible_occupations: list[str] # ["All"] or ["Farmer"] etc.
    tags: list[str] = field(default_factory=list)

    def short_description(self, max_chars: int = 120) -> str:
        """Return a truncated description for list views."""
        if len(self.description) <= max_chars:
            return self.description
        return self.description[:max_chars].rstrip() + "…"
