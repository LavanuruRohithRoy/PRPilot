from typing import Literal

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Explicit standard error payload contract."""

    detail: str = Field(
        ...,
        description="Human-readable explanation of the error occurrence.",
    )
    code: Literal["ENTITY_NOT_FOUND", "DOMAIN_VALIDATION_ERROR"] = Field(
        ...,
        description="Unique machine-readable uppercase code classification.",
    )
    meta: dict[str, str] | None = Field(
        default=None,
        description="Optional diagnostic key-value details.",
    )
