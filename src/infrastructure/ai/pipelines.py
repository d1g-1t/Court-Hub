from __future__ import annotations

import hashlib
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx
import orjson
import structlog

from src.core.config import Settings

logger = structlog.get_logger(__name__)

PROMPTS_DIR = Path(__file__).parent / "prompts"

PROMPT_VERSION = "1.0.0"


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        return f"[prompt {name} not found]"
    return path.read_text(encoding="utf-8")


def _prompt_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


class AIPipelineRunner:

    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_chat_model
        self.timeout = settings.ai_review_timeout_seconds

    async def _call_ollama(self, prompt: str, context: str) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "prompt": f"{prompt}\n\n---\n\n{context}",
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 4096},
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/api/generate", json=payload)
                resp.raise_for_status()
                data = resp.json()
                return {
                    "response": data.get("response", ""),
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                }
        except Exception as exc:
            logger.warning("ollama_call_failed", error=str(exc))
            return {
                "response": f"[AI unavailable: {exc}]",
                "prompt_tokens": 0,
                "completion_tokens": 0,
            }

    async def run_pipeline(
        self,
        *,
        pipeline_type: str,
        matter_id: UUID,
        context_data: dict[str, Any],
    ) -> dict[str, Any]:

        prompt_name_map = {
            "CASE_SUMMARY": "case_summary_prompt",
            "CHRONOLOGY_BUILDER": "chronology_builder_prompt",
            "INCONSISTENCY_DETECTION": "inconsistency_detection_prompt",
            "HEARING_MEMO": "hearing_memo_prompt",
            "RISK_REVIEW": "risk_review_prompt",
        }

        prompt_name = prompt_name_map.get(pipeline_type, "case_summary_prompt")
        prompt_text = _load_prompt(prompt_name)
        p_hash = _prompt_hash(prompt_text)

        context_str = orjson.dumps(context_data, option=orjson.OPT_INDENT_2).decode()

        start = time.monotonic()
        result = await self._call_ollama(prompt_text, context_str)
        latency_ms = int((time.monotonic() - start) * 1000)

        return {
            "matter_id": str(matter_id),
            "pipeline_type": pipeline_type,
            "model_name": self.model,
            "prompt_hash": p_hash,
            "prompt_version": PROMPT_VERSION,
            "input_snapshot": context_data,
            "output_snapshot": {"text": result["response"]},
            "status": "COMPLETED",
            "latency_ms": latency_ms,
            "prompt_tokens": result["prompt_tokens"],
            "completion_tokens": result["completion_tokens"],
            "created_at": datetime.now(UTC).isoformat(),
        }
