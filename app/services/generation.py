from __future__ import annotations

import json
import logging
import os
import re

from app.config import settings
from huggingface_hub import InferenceClient


def generation_enabled() -> bool:
    return bool(settings.hf_api_token and settings.generation_model)


def generate_interview_questions(resume_text: str, job_description: str | None) -> list[str]:
    if not generation_enabled():
        return []
    prompt = (
        f"Based on the following resume and job description, generate 5 concise interview questions.\n\n"
        f"Resume:\n{resume_text[:3000]}\n\n"
        f"Job Description:\n{job_description or ''}\n\n"
        "Return only a JSON list of strings, no extra text."
    )
    return _call_generation(prompt, expected_type="list")


def generate_suggestions(analysis_summary: dict) -> list[str]:
    if not generation_enabled():
        return []
    prompt = (
        "Given the following CV analysis summary, suggest 3 actionable improvements for the candidate.\n"
        f"Summary: {analysis_summary}\n\n"
        "Return only a JSON list of strings, no extra text."
    )
    return _call_generation(prompt, expected_type="list")


def _call_generation(prompt: str, expected_type: str = "list") -> list[str]:
    generated = _hf_generate(prompt)
    if not generated:
        return []
    # Try to extract JSON list from the output
    match = re.search(r"\[.*\]", generated, re.DOTALL)
    if match:
        parsed = json.loads(match.group())
        if isinstance(parsed, list):
            return [str(item) for item in parsed[:5]]
    # Fallback: return empty list
    return []


def _hf_generate(prompt: str) -> str | None:
    if not settings.generation_model or not settings.hf_api_token:
        return None
    try:
        client = InferenceClient(api_key=settings.hf_api_token)
        out = None
        # Prefer chat/completions for conversational models
        try:
            chat_fn = getattr(client, "chat_completion", None)
            if callable(chat_fn):
                resp = chat_fn(
                    model=settings.generation_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=256,
                    temperature=0.7,
                )
                if hasattr(resp, "choices") and resp.choices:
                    msg = resp.choices[0].message
                    out = getattr(msg, "content", None)
                elif isinstance(resp, dict):
                    choices = resp.get("choices") or []
                    if choices and isinstance(choices[0], dict):
                        out = ((choices[0].get("message") or {}) or {}).get("content")
        except Exception:
            out = None

        if not out:
            out = client.text_generation(
                prompt,
                model=settings.generation_model,
                max_new_tokens=256,
                temperature=0.7,
                return_full_text=False,
            )
        return out if isinstance(out, str) else None
    except Exception as e:  # noqa: BLE001
        logging.getLogger(__name__).warning(f"HF generation failed: {e}")
        return None
