from __future__ import annotations

import re

PII_PATTERNS = [
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    r"\+?\d{7,15}",
    r"\b\d{4}-\d{2}-\d{2}\b",
    r"\b\d{2}/\d{2}/\d{2,4}\b",
]

PII_RE = re.compile("|".join(PII_PATTERNS))


def strip_pii_for_models(text: str) -> str:
    return PII_RE.sub("[REDACTED]", text or "")
