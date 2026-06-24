# CourtHub

> An enterprise legal-ops backend that handles everything from matter lifecycle to AI-powered case intelligence — built with FastAPI, PostgreSQL, and a sprinkle of async magic.

---

## What this is

A production-grade FastAPI service for managing litigation portfolios. Think of it as the engine room behind a legal department: matters flow in, deadlines get tracked, hearings get scheduled, evidence gets catalogued, and when things get hairy the AI pipeline synthesises the chaos into something your GC can actually read.

Built with Clean Architecture + DDD so the domain logic doesn't bleed into routing, and the routing doesn't know what a database is.

---

## Tech stack

| Layer | Technology |
|---|---|
| API | FastAPI 0.115+, Uvicorn, ORJSON |
| DB | PostgreSQL 16 (asyncpg), SQLAlchemy 2.0 async |
| Cache | Redis 7 (cache-aside, TTL-based) |
| Queue | Celery 5 + Redis broker, 5 named queues |
| Auth | PASETO v4.local (pyseto), bcrypt |
| AI | Ollama (local LLMs), 5 prompt pipelines |
| Observability | Prometheus, Grafana Tempo, Loki, Grafana |
| Config | pydantic-settings, `.env` |
| Logging | structlog (JSON in prod, pretty in dev) |

---

## Ports (non-standard to avoid conflicts)

| Service | Port |
|---|---|
| API | **8099** |
| PostgreSQL | **5499** |
| Redis | **6399** |
| Ollama | **11499** (host→container 11434) |
| Flower | **5599** |
| Prometheus | **9099** |
| Grafana | **3099** |
| Tempo gRPC | **4399** |
| Tempo HTTP | **3299** |
| Loki | **3199** |

---

## Quick start

### Prerequisites

- Docker Desktop (or Podman) with Compose v2
- GNU Make (ships with Git for Windows / WSL / macOS)

### 1 — First time setup

```bash
make setup
```

This copies `.env.example` → `.env`. Open it and set `PASETO_SECRET_KEY` to exactly 32 bytes of random stuff.

### 2 — Spin everything up

```bash
make up
```

First run pulls images and builds the API container. Ollama will download whatever model is set in `OLLAMA_CHAT_MODEL` on first use.

### 3 — Run migrations

```bash
make migrate
```

### 4 — Check it's alive

```
GET http://localhost:8099/api/v1/health/live
```

Interactive docs: http://localhost:8099/docs

Grafana dashboards: http://localhost:3099 (admin / admin)

Flower (Celery monitor): http://localhost:5599

---

## Development

```bash
# Install dev deps (needs Python 3.12+)
pip install -e ".[dev]"

# Lint
make lint

# Tests (uses aiosqlite, no docker required)
make test

# Watch logs from all containers
make logs
```

### Running locally without Docker

```bash
# You still need PG + Redis running somewhere (or use docker-compose for just those)
docker compose up -d postgres redis

# Then
uvicorn src.main:app --reload --port 8099
```

---

## Project structure

```
src/
├── core/               # Config, security, logging — framework-agnostic primitives
├── domain/             # Pure Python: entities, value objects, repo ABCs, domain services
├── infrastructure/
│   ├── database/       # SQLAlchemy models + concrete repos
│   ├── ai/             # Ollama pipeline runner + prompt files
│   ├── cache/          # Redis cache service
│   ├── queue/          # Celery app, task definitions, beat schedule
│   ├── integrations/   # Court system API stubs
│   └── observability/  # Prometheus metric counters / histograms
├── application/
│   ├── dto.py          # All Pydantic v2 request/response schemas
│   └── use_cases/      # One module per feature slice (auth, matters, deadlines, …)
└── presentation/
    ├── deps.py         # FastAPI dependency injection wiring
    ├── middleware.py   # Request context + domain → HTTP exception mapping
    └── api/v1/         # One router file per resource

alembic/                # Async migrations (env.py + versions/)
tests/                  # pytest-asyncio, httpx AsyncClient, SQLite in-memory
docker/                 # Dockerfile (multi-stage), prometheus.yml, tempo.yml, grafana/
```

---

## Auth flow

1. `POST /api/v1/auth/login` → returns `access_token` (PASETO v4.local, 30 min) + `refresh_token` (14 days)
2. Pass `Authorization: Bearer <access_token>` on every protected request
3. When access token expires: `POST /api/v1/auth/refresh`

---

## AI pipelines

Five prompt-driven pipelines sit under `POST /api/v1/ai/{pipeline}`:

| Pipeline | What it does |
|---|---|
| `case-summary` | Produces an executive summary of the matter |
| `chronology-builder` | Extracts a structured timeline from free text |
| `inconsistency-detection` | Flags contradictions between documents |
| `hearing-memo` | Generates a concise hearing prep memo |
| `risk-review` | Scores legal risk and highlights key exposure areas |

All prompts are structured to return JSON so the output is machine-readable and immediately persisted as an `AIAnalysisRun` record with full audit trail.

---

## Background tasks

Celery beat fires three scheduled jobs:

- **deadline_risk_scan** — every 15 minutes, creates alerts for approaching/overdue deadlines
- **portfolio_analytics** — hourly, refreshes Redis-cached portfolio stats
- **outside_counsel_spend_rollup** — daily, aggregates spend per matter

Ad-hoc tasks (court import, chronology generation, inconsistency check) are dispatched on demand via the API.

---

## Make targets

```
make setup    — copy .env.example → .env
make up       — docker compose up -d (build if needed)
make down     — docker compose down
make migrate  — run alembic upgrade head
make test     — pytest with coverage
make lint     — ruff check + ruff format --check
make logs     — tail all container logs
```

---

## Contributing / notes

This codebase follows strict async patterns — every DB call goes through `AsyncSession`, every Redis hit is awaited. If you add a new feature, start from the domain layer (entities + repo ABC) and work outwards. The use-cases layer is where business rules live; routers should be thin wrappers.

N+1 queries are prevented via `selectinload` for collections and `joinedload` for single-entity lookups. If you add a relationship to `MatterModel`, make sure it has a deliberate loading strategy (`lazy="noload"` by default, load explicitly where needed).

Run `mypy` before you push. The `strict = true` config is there for a reason.
