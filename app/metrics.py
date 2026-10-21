"""Prometheus metrics instrumentation for FastAPI.

Exposes operational monitoring metrics at /metrics endpoint using
prometheus-fastapi-instrumentator.
"""

from fastapi import FastAPI
from prometheus_client import Info
from prometheus_fastapi_instrumentator import Instrumentator

from app.settings import get_settings


def setup_metrics(app: FastAPI) -> None:
    """Initialize Prometheus metrics instrumentation for the FastAPI app.

    Args:
        app: The FastAPI application instance
    """
    settings = get_settings()
    if not settings.metrics_enabled:
        return

    # Exclude the metrics endpoint itself from its own instrumentation.
    Instrumentator(
        excluded_handlers=[settings.metrics_path],
        should_group_status_codes=True,
        should_round_latency_decimals=False,
    ).instrument(app).expose(
        app,
        include_in_schema=False,
        endpoint=settings.metrics_path,
    )

    # Build/runtime identity labels for dashboards and alerts.
    build_info = Info(
        "ai_image_understanding_engine_build",
        "Build and runtime information for the image understanding engine.",
        labelnames=["app", "version", "environment"],
    )
    build_info.labels(
        app=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    ).info({})


def get_metrics_endpoint() -> str:
    """Return the configured metrics endpoint path."""
    return get_settings().metrics_path
