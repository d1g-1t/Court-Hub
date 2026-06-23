from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Settings
from src.domain.exceptions import NotFoundError
from src.infrastructure.ai.pipelines import AIPipelineRunner
from src.infrastructure.database.models import AIAnalysisRunModel, ChronologyEventModel
from src.infrastructure.database.repositories import (
    AIRunSQLRepository,
    ChronologySQLRepository,
    MatterSQLRepository,
)
from src.infrastructure.observability.metrics import AI_PIPELINE_DURATION, AI_RUNS_TOTAL


async def run_ai_pipeline(
    matter_id: UUID,
    pipeline_type: str,
    *,
    session: AsyncSession,
    settings: Settings,
) -> AIAnalysisRunModel:
    matter_repo = MatterSQLRepository(session)
    matter = await matter_repo.get_by_id(matter_id)
    if not matter:
        raise NotFoundError("Matter", matter_id)

    context_data = {
        "matter_number": matter.matter_number,
        "title": matter.title,
        "matter_type": matter.matter_type,
        "court_system": matter.court_system,
        "status": matter.status,
        "risk_level": matter.risk_level,
        "role_in_case": matter.role_in_case,
    }

    runner = AIPipelineRunner(settings)
    AI_RUNS_TOTAL.labels(pipeline_type=pipeline_type).inc()

    import time
    start = time.monotonic()
    result = await runner.run_pipeline(
        pipeline_type=pipeline_type,
        matter_id=matter_id,
        context_data=context_data,
    )
    elapsed = time.monotonic() - start
    AI_PIPELINE_DURATION.labels(pipeline_type=pipeline_type).observe(elapsed)

    repo = AIRunSQLRepository(session)
    run_model = AIAnalysisRunModel(
        matter_id=matter_id,
        pipeline_type=result["pipeline_type"],
        model_name=result["model_name"],
        prompt_hash=result["prompt_hash"],
        prompt_version=result["prompt_version"],
        input_snapshot=result["input_snapshot"],
        output_snapshot=result["output_snapshot"],
        status=result["status"],
        latency_ms=result["latency_ms"],
        prompt_tokens=result["prompt_tokens"],
        completion_tokens=result["completion_tokens"],
    )
    run_model = await repo.create(run_model)
    return run_model


async def generate_chronology(
    matter_id: UUID,
    *,
    session: AsyncSession,
    settings: Settings,
    min_confidence: float = 0.60,
) -> list[ChronologyEventModel]:
    run = await run_ai_pipeline(
        matter_id, "CHRONOLOGY_BUILDER", session=session, settings=settings
    )

    import orjson
    events: list[ChronologyEventModel] = []
    output_text = run.output_snapshot.get("text", "")

    try:
        parsed = orjson.loads(output_text)
        raw_events = parsed.get("events", [])
    except Exception:
        raw_events = []

    chrono_repo = ChronologySQLRepository(session)
    for evt in raw_events:
        confidence = evt.get("confidence", 0.5)
        if confidence < min_confidence:
            continue
        chrono = ChronologyEventModel(
            matter_id=matter_id,
            event_at=evt.get("date", run.created_at),
            title=evt.get("title", "Unknown event"),
            description=evt.get("description", ""),
            source_type=evt.get("source_type", "ai"),
            ai_generated=True,
            confidence=confidence,
        )
        chrono = await chrono_repo.create(chrono)
        events.append(chrono)

    return events


async def list_chronology(
    matter_id: UUID,
    *,
    session: AsyncSession,
) -> list[ChronologyEventModel]:
    repo = ChronologySQLRepository(session)
    return await repo.list_by_matter(matter_id)
