from __future__ import annotations

from uuid import UUID


class DomainError(Exception):

    def __init__(self, message: str = "Domain error") -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(DomainError):

    def __init__(self, entity: str, entity_id: UUID | str) -> None:
        super().__init__(f"{entity} {entity_id} not found")
        self.entity = entity
        self.entity_id = entity_id


class DuplicateError(DomainError):

    def __init__(self, entity: str, field: str, value: str) -> None:
        super().__init__(f"{entity} with {field}={value!r} already exists")


class AuthenticationError(DomainError):

    def __init__(self, detail: str = "Authentication failed") -> None:
        super().__init__(detail)


class AuthorizationError(DomainError):

    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(detail)


class InvalidStateTransitionError(DomainError):

    def __init__(self, entity: str, current: str, target: str) -> None:
        super().__init__(
            f"Cannot transition {entity} from {current!r} to {target!r}"
        )


class DeadlinePolicyViolation(DomainError):


class AIOutputError(DomainError):
