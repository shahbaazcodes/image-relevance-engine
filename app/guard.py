"""Mismatch Guard safety module enforcing thresholds.

Ensures that search results and image processing operations comply with
configured safety thresholds. Guards against spurious results and out-of-bounds
similarity scores from the search engine and ingestion pipeline.
"""

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.settings import get_settings

router = APIRouter(prefix="/guard", tags=["Mismatch Guard"])


class GuardRequest(BaseModel):
    """Request payload for a guard evaluation."""

    query_category: str
    matched_category: str
    similarity_score: float


class GuardResponse(BaseModel):
    """Verdict returned by the mismatch guard."""

    passed: bool
    reason: str


class MismatchGuard:
    """Validates search and ingestion results against configured thresholds.

    The guard intercepts search and ingestion outputs and rejects any
    results that do not meet minimum quality or confidence criteria.
    """

    def __init__(self):
        self._settings = get_settings()
        self._blocked_threshold = self._settings.guard_block_threshold
        self._min_confidence = self._settings.guard_min_confidence
        self._top_k = self._settings.guard_top_k

    def validate_similarity(self, similarity: float) -> bool:
        """Validate that a similarity score is within acceptable bounds.

        Args:
            similarity: Combined similarity score from 0.0 to 1.0

        Returns:
            True if the score passes all thresholds
        """
        if not 0.0 <= similarity <= 1.0:
            return False
        return similarity >= self._min_confidence and similarity >= self._blocked_threshold

    def validate_category_confidence(self, category: str, confidence: float) -> bool:
        """Validate that a category assignment has adequate confidence.

        Args:
            category: Assigned category label
            confidence: Confidence score for the category assignment

        Returns:
            True if the category assignment is valid
        """
        if not category or not isinstance(category, str):
            return False
        return confidence >= self._min_confidence

    def validate_top_k_results(
        self,
        results: list[dict[str, Any]],
        expected_count: int | None = None,
    ) -> list[dict[str, Any]]:
        """Filter results to only those that meet guard thresholds.

        Args:
            results: List of search results from the HybridSearchEngine
            expected_count: Desired number of results to keep (defaults to guard_top_k)

        Returns:
            Filtered list of valid results
        """
        limit = expected_count if expected_count is not None else self._top_k
        valid: list[dict[str, Any]] = []
        for result in results:
            if len(valid) >= limit:
                break
            similarity = result.get("similarity", 0.0)
            if not self.validate_similarity(similarity):
                continue
            category = result.get("category", "")
            confidence = similarity
            if not self.validate_category_confidence(category, confidence):
                continue
            # Remove any internal guard fields
            clean_result = {k: v for k, v in result.items() if k not in ("_guard_valid",)}
            valid.append(clean_result)
        return valid

    def validate_search_request(self, query: str, limit: int = 10) -> bool:
        """Validate a search request before execution.

        Args:
            query: Search query string
            limit: Desired number of results

        Returns:
            True if the request passes pre-flight checks
        """
        if not query or not isinstance(query, str) or not query.strip():
            return False
        return isinstance(limit, int) and 1 <= limit <= 100

    async def apply_guard(
        self,
        results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Apply full guard validation to search results.

        Args:
            results: Raw results from search engine

        Returns:
            Guard-validated results ready for API response
        """
        return self.validate_top_k_results(results)


# Module-level singleton guard
guard = MismatchGuard()


@router.post("/evaluate", response_model=GuardResponse)
async def evaluate_mismatch(request: GuardRequest):
    """Evaluate a match against the Mismatch Guard thresholds.

    Args:
        request: Query category, matched category and similarity score

    Returns:
        GuardResponse indicating whether the match is safe to surface
    """
    if request.query_category.lower() != request.matched_category.lower():
        return GuardResponse(passed=False, reason="Category mismatch detected")
    if not guard.validate_similarity(request.similarity_score):
        return GuardResponse(
            passed=False,
            reason=f"Similarity score below safety threshold ({guard._min_confidence})",
        )
    return GuardResponse(passed=True, reason="Matched safety constraints")
