from __future__ import annotations

import json
import logging
import re
from typing import Any

from app.config import settings
from huggingface_hub import InferenceClient


def structured_extraction_enabled() -> bool:
    return bool(settings.hf_api_token and settings.structured_extraction_model and settings.enable_structured_extraction)


def extract_structured_cv(resume_text: str) -> dict[str, Any] | None:
    if not structured_extraction_enabled():
        return None

    schema = {
        "personal_details": {
            "full_name": None,
            "email": None,
            "phone": None,
            "address": None,
            "dob": None,
            "linkedin": None,
            "github": None,
            "portfolio": None,
        },
        "education_details": {"education": [], "certifications": [], "languages": []},
        "professional_details": {
            "skills": [],
            "experience": [],
            "position": "",
            "previous_companies": [],
            "bio": "",
        },
    }

    prompt = "\n".join(
        [
            "You are a strict information extraction system.",
            "Task: Extract data from RESUME into the exact JSON schema.",
            "Rules:",
            "- Output ONLY a single valid JSON object.",
            "- No markdown, no code fences, no explanations.",
            "- Do not invent facts.",
            "- Use null for unknown scalars and [] for unknown lists.",
            "- Keep strings short and verbatim when possible.",
            "",
            "JSON_SCHEMA:",
            json.dumps(schema, ensure_ascii=False),
            "",
            "RESUME:",
            (resume_text or "")[:20000],
        ]
    )

    try:
        client = InferenceClient(api_key=settings.hf_api_token)
        generated = None
        # Prefer chat/completions for instruction-tuned models served as conversational
        try:
            chat_fn = getattr(client, "chat_completion", None)
            if callable(chat_fn):
                resp = chat_fn(
                    model=settings.structured_extraction_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=900,
                    temperature=0.0,
                )
                # huggingface_hub may return an object with .choices[0].message.content or a dict
                if hasattr(resp, "choices") and resp.choices:
                    msg = resp.choices[0].message
                    generated = getattr(msg, "content", None)
                elif isinstance(resp, dict):
                    choices = resp.get("choices") or []
                    if choices and isinstance(choices[0], dict):
                        generated = ((choices[0].get("message") or {}) or {}).get("content")
        except Exception:
            generated = None

        if not generated:
            generated = client.text_generation(
                prompt,
                model=settings.structured_extraction_model,
                max_new_tokens=900,
                temperature=0.0,
                return_full_text=False,
            )

        if not generated or not isinstance(generated, str):
            return None

        parsed = _parse_first_json_object(generated)
        if not isinstance(parsed, dict):
            return None

        if not _looks_like_structured_data(parsed):
            return None

        normalized = _normalize_structured_data(parsed)
        return normalized
    except Exception as e:  # noqa: BLE001
        logging.getLogger(__name__).warning(f"HF structured extraction failed: {e}")
        return None


def _parse_first_json_object(text: str) -> Any:
    t = _cleanup_model_text(text)
    try:
        return json.loads(t)
    except Exception:
        pass

    m = re.search(r"\{.*\}", t, re.DOTALL)
    if not m:
        return None

    try:
        candidate = m.group(0)
        if settings.structured_extraction_repair_json:
            candidate = _repair_json(candidate)
        return json.loads(candidate)
    except Exception:
        return None


def _cleanup_model_text(text: str) -> str:
    t = (text or "").strip()
    t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s*```$", "", t)
    t = t.replace("\u201c", '"').replace("\u201d", '"').replace("\u2019", "'")
    if settings.structured_extraction_repair_json:
        t = _repair_json(t)
    return t.strip()


def _repair_json(text: str) -> str:
    t = text
    t = re.sub(r",\s*([}\]])", r"\1", t)
    return t


def _looks_like_structured_data(d: dict[str, Any]) -> bool:
    if not isinstance(d, dict):
        return False
    if not isinstance(d.get("personal_details"), dict):
        return False
    if not isinstance(d.get("education_details"), dict):
        return False
    if not isinstance(d.get("professional_details"), dict):
        return False
    return True


def _normalize_structured_data(d: dict[str, Any]) -> dict[str, Any]:
    # Ensure expected list types and trim strings
    for section in ("personal_details", "education_details", "professional_details"):
        sec = d.get(section, {})
        if not isinstance(sec, dict):
            d[section] = {}
            continue
        for k, v in sec.items():
            if isinstance(v, str):
                d[section][k] = v.strip() or None
            elif isinstance(v, list):
                d[section][k] = [str(item).strip() for item in v if item]
            else:
                d[section][k] = v
    return d
