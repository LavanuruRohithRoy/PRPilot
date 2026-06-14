from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import DomainValidationError, EntityNotFoundError
from app.schemas.errors import ErrorResponse


async def entity_not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle EntityNotFoundError by returning a 404 status."""
    response_data = ErrorResponse(
        detail=str(exc),
        code="ENTITY_NOT_FOUND",
    )
    return JSONResponse(
        status_code=404,
        content=response_data.model_dump(),
    )


async def domain_validation_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle DomainValidationError by returning a 422 status."""
    response_data = ErrorResponse(
        detail=str(exc),
        code="DOMAIN_VALIDATION_ERROR",
    )
    return JSONResponse(
        status_code=422,
        content=response_data.model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on the FastAPI application."""
    app.add_exception_handler(EntityNotFoundError, entity_not_found_handler)
    app.add_exception_handler(DomainValidationError, domain_validation_handler)
