"""
exceptions.py — Custom exceptions for the Government Scheme Discovery Assistant.
"""


class SchemeNotFoundError(Exception):
    """Raised when a scheme ID is not found in the repository."""

    def __init__(self, scheme_id: str) -> None:
        super().__init__(f"Scheme with id '{scheme_id}' was not found.")
        self.scheme_id = scheme_id


class InvalidProfileError(Exception):
    """Raised when a UserProfile is constructed with logically invalid data."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
