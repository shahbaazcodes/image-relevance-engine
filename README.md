# AI Image Understanding & Content Matching API

A fully local, zero-dependency developer stack for hybrid image-relevance search,
content matching and mismatch guarding. Built on FastAPI, PostgreSQL + pgvector
(full-text **and** vector fusion), Redis (cache + ARQ queue), LocalStack (S3), an
MCP server and Prometheus metrics.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"   # or: uv sync --frozen && uv run dev
docker compose up -d      # postgres (pgvector), redis, localstack
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Endpoints:

| Method | Path                  | Description                          |
|--------|-----------------------|--------------------------------------|
| GET    | /health               | Liveness + backing service status    |
| GET    | /metrics              | Prometheus metrics                   |
| GET    | /search/hybrid         | Hybrid search (lexical + vector fusion) |
| GET    | /search/categories     | Catalog categories                   |
| POST   | /ingest/upload         | Ingest + pHash near-duplicate detection |
| POST   | /guard/evaluate        | Mismatch Guard evaluation             |
| GET    | /guard/evaluate        | Guard evaluator via MCP/HTTP         |

## Evaluation

Run the deterministic hybrid-search benchmark and write results to
`EVIDENCE.md`:

```bash
python3 eval/eval.py
```

The evaluator hits `http://127.0.0.1:8000/search/hybrid` across 20 queries
(five per category: fox, wolf, dog, deer) and computes overall Top-1 precision.

## Configuration

Env vars are loaded from `.env` (see `.env.example`). Default database is
`postgresql+asyncpg://postgres:postgres@localhost:5432/image_relevance_db`.

## Deployment

`deploy_aws.sh` produces a production packaging manifest (ECR repo
`image-relevance-engine`, S3 bucket `image-relevance-assets-prod`).
