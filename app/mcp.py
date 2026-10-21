from typing import Any

import httpx
from fastmcp import FastMCP

mcp = FastMCP("Image Relevance API")


@mcp.tool()
async def hybrid_search(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Perform hybrid search combining text and image embeddings

    Args:
        query: The search query or caption
        limit: Maximum number of results to return (default: 10)

    Returns:
        List of search results with id, filename, category, and similarity score
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://127.0.0.1:8000/search/hybrid",
            params={"query": query, "limit": limit},
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_categories() -> list[str]:
    """Get available categories in the database

    Returns:
        List of animal categories
    """
    # Mock categories - in real implementation, this would query the database
    return ["fox", "wolf", "dog", "deer"]


@mcp.tool()
async def evaluate_search(query: str, expected_category: str, limit: int = 5) -> dict[str, Any]:
    """Perform search and evaluate results against expected category

    Args:
        query: The search query
        expected_category: The expected animal category
        limit: Maximum number of results to return

    Returns:
        Dictionary containing search results and evaluation metrics
    """
    results = await hybrid_search(query, limit)

    # Find top-1 result
    top_result = results[0] if results else None

    # Check if top result matches expected category
    matched = False
    if top_result:
        matched = top_result.get("category") == expected_category

    return {
        "query": query,
        "expected_category": expected_category,
        "results": results,
        "top_match": top_result,
        "is_correct": matched,
        "total_results": len(results),
    }


if __name__ == "__main__":
    mcp.run()
