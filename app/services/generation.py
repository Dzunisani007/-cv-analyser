from __future__ annotations

import logging
import os

import requests

from app.config import settings


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
    headers = {
        "Authorization": f"Bearer {settings.hf_api_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 256, "temperature": 0.7},
    }
    try:
        resp = requests.post(
            f"https://api-inference.huggingface.co/models/{settings.generation_model}",
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        # HF API returns list with generated_text
        if isinstance(data, list) and data and "generated_text" in data[0]:
            generated = data[0]["generated_text"]
            # Try to extract JSON list from the output
            import json
            import re

            match = re.search(r"\[.*\]", generated, re.DOTALL)
            if match:
                parsed = json.loads(match.group())
                if isinstance(parsed, list):
                    return [str(item) for item in parsed[:5]]
        # Fallback: return empty list
        return []
    except Exception as e:
        logging.getLogger(__name__).warning(f"HF generation failed: {e}")
        return []
