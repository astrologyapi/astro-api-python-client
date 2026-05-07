"""
Tarot namespace.

Tarot card readings and predictions.
"""

from typing import Any


class TarotNamespace:
    """Tarot endpoints."""

    def __init__(self, http_client: Any) -> None:
        self.http = http_client

    def _post(self, endpoint: str, body: dict[str, Any]) -> Any:
        return self.http.post(endpoint, body)

    def get_predictions(
        self,
        love: int = 12,
        career: int = 23,
        finance: int = 45,
    ) -> dict[str, Any]:
        """General tarot card reading — draws cards with interpretations for past, present, and future."""
        return self._post(
            "tarot_predictions",
            {
                "love": love,
                "career": career,
                "finance": finance,
            },
        )

    def get_yes_no(self, tarot_id: int = 5) -> dict[str, Any]:
        """Yes/No tarot reading — a single card draw with a clear yes or no answer."""
        return self._post("yes_no_tarot", {"tarot_id": tarot_id})
