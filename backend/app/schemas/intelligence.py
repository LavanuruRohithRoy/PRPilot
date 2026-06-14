from pydantic import BaseModel


class GroundedCitation(BaseModel):
    """Schema representing source attribution metadata for grounded intelligence."""

    id: str
    title: str
    url: str | None = None
    score: float | None = None
    reference: str | None = None


class GroundedQueryResponse(BaseModel):
    """Schema representing a verified grounded question answering response."""

    query: str
    answer: str
    citations: list[GroundedCitation]
