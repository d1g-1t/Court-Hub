from __future__ import annotations

from typing import Any
from uuid import UUID as _UUID

from sqlalchemy import JSON, String, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID


class CompatJSONB(TypeDecorator):
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())


class CompatUUID(TypeDecorator):
    impl = String(36)
    cache_ok = True

    @property
    def python_type(self) -> type[_UUID]:
        return _UUID

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value: _UUID | str | None, dialect: Any) -> Any:
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value if isinstance(value, _UUID) else _UUID(value)
        return str(value)

    def process_result_value(self, value: Any, dialect: Any) -> _UUID | None:
        if value is None:
            return None
        if isinstance(value, _UUID):
            return value
        return _UUID(value)
