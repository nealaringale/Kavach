"""Small, deterministic helpers used by the Kavach1930 MVP."""

from __future__ import annotations

import json
import re
from typing import Any


# These local patterns reduce exposure, but cannot identify every kind of PII.
_PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", re.IGNORECASE)
_EMAIL_PATTERN = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    re.IGNORECASE,
)
_INDIAN_PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)"
)
_AADHAAR_LABELLED_PATTERN = re.compile(
    r"\b(?:aadhaar|aadhar|uidai|uid)\s*(?:number|no\.?|#)?\s*[:\-]?\s*"
    r"\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    re.IGNORECASE,
)
_ACCOUNT_LABELLED_PATTERN = re.compile(
    r"\b(?:bank\s+)?account\s*(?:number|no\.?|#)\s*[:\-]?\s*"
    r"\d{8,18}\b",
    re.IGNORECASE,
)
_CARD_LABELLED_PATTERN = re.compile(
    r"\b(?:card|debit card|credit card)\s*(?:number|no\.?|#)\s*[:\-]?\s*"
    r"(?:\d[ -]?){13,19}\b",
    re.IGNORECASE,
)


def redact_sensitive_data(text: str) -> str:
    """Mask common Indian identifiers before sending evidence to Gemini.

    This is conservative and intentionally does not redact every 12-digit
    sequence because transaction references in the demo may also be 12 digits.
    It is not a complete PII detector.
    """
    redacted = _PAN_PATTERN.sub("[REDACTED PAN]", text)
    redacted = _EMAIL_PATTERN.sub("[REDACTED EMAIL]", redacted)
    redacted = _AADHAAR_LABELLED_PATTERN.sub("[REDACTED AADHAAR]", redacted)
    redacted = _ACCOUNT_LABELLED_PATTERN.sub("[REDACTED ACCOUNT NUMBER]", redacted)
    redacted = _CARD_LABELLED_PATTERN.sub("[REDACTED CARD NUMBER]", redacted)
    redacted = _INDIAN_PHONE_PATTERN.sub("[REDACTED PHONE]", redacted)
    return redacted


INJECTION_PATTERNS: dict[str, str] = {
    "Instruction override": (
        r"\bignore\s+(?:all\s+)?(?:previous|prior|earlier)\s+instructions\b"
    ),
    "Prompt or secret extraction": (
        r"\b(?:reveal|print|show|expose|repeat)\b.{0,80}"
        r"\b(?:system prompt|developer message|api key|secret)\b"
    ),
    "Rule bypass": (
        r"\b(?:disregard|override|bypass)\b.{0,80}"
        r"\b(?:rules|instructions|safety|policy)\b"
    ),
    "Forced-safe classification": (
        r"\b(?:classify|report|output|mark)\b.{0,50}\b(?:safe|legitimate)\b"
    ),
}


def detect_instruction_signals(text: str) -> list[str]:
    """Return configured phrase-pattern matches; this is not a full defense."""
    return [
        label
        for label, pattern in INJECTION_PATTERNS.items()
        if re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    ]


def parse_json_response(text: str) -> dict[str, Any]:
    """Parse a JSON object, tolerating a Markdown JSON code fence."""
    cleaned = (text or "").strip()

    if cleaned.startswith(chr(96) * 3):
        cleaned = re.sub(r"^\x60{3}(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*\x60{3}$", "", cleaned)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        # Some models add a short preamble despite being asked for JSON.
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("The model did not return a JSON object.") from None
        try:
            parsed = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError("The model returned invalid JSON.") from exc

    if not isinstance(parsed, dict):
        raise TypeError("The model response must be a JSON object.")
    return parsed


def is_exact_source_match(value: Any, source: str) -> bool:
    """True only when a non-empty string appears verbatim in source text."""
    return isinstance(value, str) and bool(value.strip()) and value.strip() in source


def as_text(value: Any, default: str = "") -> str:
    """Convert safe scalar values to text without leaking containers into UI."""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)):
        return str(value)
    return default


def normalise_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    """Apply basic shape and length bounds before rendering model output."""
    allowed_risks = {"HIGH", "MEDIUM", "LOW", "UNCERTAIN"}
    risk = as_text(payload.get("risk_level"), "UNCERTAIN").upper()
    if risk not in allowed_risks:
        risk = "UNCERTAIN"

    def dict_items(value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, dict)][:30]

    def text_items(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [as_text(item) for item in value if isinstance(item, (str, int, float))][:30]

    safe_warnings = []
    for item in dict_items(payload.get("warning_signs", [])):
        safe_warnings.append({
            "title": as_text(item.get("title"), "Finding")[:180],
            "evidence_quote": as_text(item.get("evidence_quote"))[:1000],
            "reason": as_text(item.get("reason"))[:1200],
        })

    safe_transactions = []
    for item in dict_items(payload.get("transactions", [])):
        safe_transactions.append({
            "reference": as_text(item.get("reference"))[:100],
            "amount": as_text(item.get("amount"))[:100],
            "date_time": as_text(item.get("date_time"))[:120],
            "recipient": as_text(item.get("recipient"))[:180],
            "evidence_quote": as_text(item.get("evidence_quote"))[:1000],
        })

    return {
        "risk_level": risk,
        "assessment": as_text(payload.get("assessment"), "No assessment returned.")[:3000],
        "warning_signs": safe_warnings,
        "transactions": safe_transactions,
        "missing_information": text_items(payload.get("missing_information", [])),
        "incident_summary": as_text(payload.get("incident_summary"))[:5000],
        "next_steps": text_items(payload.get("next_steps", [])),
    }
