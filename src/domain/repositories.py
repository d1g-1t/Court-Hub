from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> T | None: ...

    @abstractmethod
    async def list_all(
        self,
        *,
        tenant_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[T]: ...

    @abstractmethod
    async def create(self, entity: T) -> T: ...

    @abstractmethod
    async def update(self, entity: T) -> T: ...

    @abstractmethod
    async def delete(self, entity_id: UUID) -> None: ...


class MatterRepository(BaseRepository[Any], ABC):

    @abstractmethod
    async def get_by_number(self, tenant_id: UUID, matter_number: str) -> Any | None: ...

    @abstractmethod
    async def list_by_status(
        self, tenant_id: UUID, status: str, *, limit: int = 50, offset: int = 0
    ) -> list[Any]: ...

    @abstractmethod
    async def count_by_status(self, tenant_id: UUID) -> dict[str, int]: ...


class DeadlineRepository(BaseRepository[Any], ABC):

    @abstractmethod
    async def list_by_matter(self, matter_id: UUID) -> list[Any]: ...

    @abstractmethod
    async def list_upcoming(
        self, tenant_id: UUID, before: datetime, *, limit: int = 50
    ) -> list[Any]: ...

    @abstractmethod
    async def list_overdue(self, tenant_id: UUID, *, limit: int = 50) -> list[Any]: ...


class HearingRepository(BaseRepository[Any], ABC):
    @abstractmethod
    async def list_by_matter(self, matter_id: UUID) -> list[Any]: ...


class EvidenceRepository(BaseRepository[Any], ABC):
    @abstractmethod
    async def list_by_matter(self, matter_id: UUID) -> list[Any]: ...


class IssueRepository(BaseRepository[Any], ABC):
    @abstractmethod
    async def list_by_matter(self, matter_id: UUID) -> list[Any]: ...


class ClaimRepository(BaseRepository[Any], ABC):
    @abstractmethod
    async def list_by_matter(self, matter_id: UUID) -> list[Any]: ...


class DefenseRepository(BaseRepository[Any], ABC):
    @abstractmethod
    async def list_by_matter(self, matter_id: UUID) -> list[Any]: ...


class ChronologyRepository(BaseRepository[Any], ABC):
    @abstractmethod
    async def list_by_matter(self, matter_id: UUID) -> list[Any]: ...


class OutsideCounselRepository(BaseRepository[Any], ABC):
    @abstractmethod
    async def list_by_matter(self, matter_id: UUID) -> list[Any]: ...


class BudgetRepository(BaseRepository[Any], ABC):
    @abstractmethod
    async def list_by_matter(self, matter_id: UUID) -> list[Any]: ...

    @abstractmethod
    async def total_spend_by_matter(self, matter_id: UUID) -> float: ...


class AlertRepository(BaseRepository[Any], ABC):
    @abstractmethod
    async def list_unacknowledged(
        self, tenant_id: UUID, *, limit: int = 50
    ) -> list[Any]: ...


class AuditRepository(BaseRepository[Any], ABC):
    @abstractmethod
    async def list_by_resource(
        self, resource_type: str, resource_id: UUID, *, limit: int = 100
    ) -> list[Any]: ...


class UserRepository(BaseRepository[Any], ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> Any | None: ...


class AIAnalysisRunRepository(BaseRepository[Any], ABC):
    @abstractmethod
    async def list_by_matter(self, matter_id: UUID) -> list[Any]: ...
