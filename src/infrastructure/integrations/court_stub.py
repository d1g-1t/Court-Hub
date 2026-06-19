from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4


class KadStubAdapter:

    async def search_case(self, case_reference: str) -> dict[str, Any] | None:
        return {
            "case_number": case_reference,
            "court": "Арбитражный суд города Москвы",
            "judge": "Иванов И.И.",
            "claimant": "ООО «Альфа»",
            "respondent": "ООО «Бета»",
            "status": "В производстве",
            "filed_at": (datetime.now(UTC) - timedelta(days=90)).isoformat(),
            "hearings": [
                {
                    "date": (datetime.now(UTC) + timedelta(days=14)).isoformat(),
                    "type": "Основное",
                    "courtroom": "Зал 312",
                }
            ],
        }

    async def fetch_hearings(self, case_reference: str) -> list[dict[str, Any]]:
        return [
            {
                "id": str(uuid4()),
                "date": (datetime.now(UTC) + timedelta(days=14)).isoformat(),
                "type": "Основное заседание",
                "courtroom": "Зал 312",
                "judge": "Иванов И.И.",
            }
        ]


class SudrfStubAdapter:

    async def search_case(self, case_reference: str) -> dict[str, Any] | None:
        return {
            "case_number": case_reference,
            "court": "Тверской районный суд города Москвы",
            "judge": "Петрова А.С.",
            "status": "Рассмотрение",
            "filed_at": (datetime.now(UTC) - timedelta(days=60)).isoformat(),
        }


class FedresursStubAdapter:

    async def check_bankruptcy(self, inn: str) -> dict[str, Any] | None:
        return {
            "inn": inn,
            "has_active_proceedings": False,
            "checked_at": datetime.now(UTC).isoformat(),
        }
