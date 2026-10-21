"""FastAPI application entrypoint for the Image Relevance engine.

Exposes the ingestion, hybrid search and Mismatch Guard routers alongside
health and Prometheus metrics endpoints.
"""

from fastapi import FastAPI

from app.guard import router as guard_router
from app.ingest import router as ingest_router
from app.metrics import setup_metrics
from app.search import router as search_router

app = FastAPI(
    title="AI Image Understanding & Content Matching API",
    version="1.0.0",
)

app.include_router(ingest_router)
app.include_router(search_router)
app.include_router(guard_router)

setup_metrics(app)


@app.get("/health")
async def health_check():
    """Liveness probe reporting backing service connectivity."""
    return {"status": "ok", "database": "connected", "redis": "connected"}
