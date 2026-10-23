"""Typed response contracts for Gemini output."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class WarningSign(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(description="Short title for a possible warning sign", max_length=180)
    evidence_quote: str = Field(
        description="Exact quote from submitted evidence, empty if unavailable",
        max_length=1000,
    )
    reason: str = Field(description="Why the quote may be concerning", max_length=1200)


class TransactionCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reference: str = Field(description="Verbatim transaction reference, or empty", max_length=100)
    amount: str = Field(description="Verbatim amount, or empty", max_length=100)
    date_time: str = Field(description="Verbatim date or time, or empty", max_length=120)
    recipient: str = Field(description="Verbatim recipient details, or empty", max_length=180)
    evidence_quote: str = Field(
        description="Exact source quote supporting these details, or empty",
        max_length=1000,
    )


class KavachAnalysis(BaseModel):
    """Structured, bounded model response for human-reviewed triage."""

    model_config = ConfigDict(extra="forbid")

    risk_level: Literal["HIGH", "MEDIUM", "LOW", "UNCERTAIN"]
    assessment: str = Field(max_length=3000)
    warning_signs: list[WarningSign] = Field(default_factory=list, max_length=30)
    transactions: list[TransactionCandidate] = Field(default_factory=list, max_length=30)
    missing_information: list[str] = Field(default_factory=list, max_length=30)
    incident_summary: str = Field(
        description="Chronological draft intended to fit the user-reviewed 1500 character field",
        max_length=1500,
    )
    next_steps: list[str] = Field(default_factory=list, max_length=30)
