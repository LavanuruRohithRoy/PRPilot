class PRPilotError(Exception):
    """Base exception class for all PRPilot application-level errors."""

    pass


class EntityNotFoundError(PRPilotError):
    """Exception raised when a requested resource is not found in the database."""

    pass


class DomainValidationError(PRPilotError):
    """Exception raised when domain constraints or invariants are violated."""

    pass
