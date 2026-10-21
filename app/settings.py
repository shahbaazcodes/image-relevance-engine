"""Pydantic settings for the Image Relevence API.

Loads configuration from environment variables with sensible defaults.
All settings are typed and validated via Pydantic BaseSettings.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Each field is populated from the environment variable of the same name in
    upper snake case, e.g. ``max_image_size_mb`` reads ``MAX_IMAGE_SIZE_MB``.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Image Relevence API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"

    # API
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "*"

    # Database (PostgreSQL)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = Field(default="postgres")
    postgres_db: str = "image_relevance_db"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # LocalStack (S3 compatible)
    localstack_host: str = "localhost"
    localstack_port: int = 4566
    localstack_access_key: str = "test"
    localstack_secret_key: str = Field(default="test")
    s3_bucket: str = "image-relevence"

    @property
    def localstack_endpoint_url(self) -> str:
        return f"http://{self.localstack_host}:{self.localstack_port}"

    # ImageHash duplicate detection
    phash_threshold: int = 5
    max_image_size_mb: int = 10

    # Hybrid search thresholds
    semantic_weight: float = 0.5
    lexical_weight: float = 0.5
    min_similarity_threshold: float = 0.3
    top_k_limit: int = 20

    # Mismatch Guard thresholds
    guard_top_k: int = 5
    guard_min_confidence: float = 0.4
    guard_block_threshold: float = 0.2

    # Prometheus
    metrics_enabled: bool = True
    metrics_path: str = "/metrics"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
