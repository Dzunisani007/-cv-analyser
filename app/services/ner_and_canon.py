from __future__ import annotations

import os
import re
import requests

from app.config import settings
from app.utils.hf_api import post_json_with_retry

_ner_pipe = None


def _use_hf_api() -> bool:
    return bool(settings.hf_api_token)


def load_ner():
    global _ner_pipe
    if _ner_pipe is not None:
        return _ner_pipe

    if (os.getenv("SKIP_MODEL_LOAD", "false") or "false").lower() == "true":
        _ner_pipe = "__skipped__"
        return _ner_pipe

    if _use_hf_api():
        _ner_pipe = "__hf_api__"
        return _ner_pipe

    from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

    tokenizer = AutoTokenizer.from_pretrained(settings.ner_model)
    model = AutoModelForTokenClassification.from_pretrained(settings.ner_model)
    _ner_pipe = pipeline("ner", model=model, tokenizer=tokenizer, grouped_entities=True)
    return _ner_pipe


def _ner_via_hf_api(texts: list[str]) -> list[dict]:
    headers = {"Authorization": f"Bearer {settings.hf_api_token}"}
    results = []
    for txt in texts:
        payload = {"inputs": txt}
        try:
            resp = post_json_with_retry(
                url=f"https://api-inference.huggingface.co/models/{settings.ner_model}",
                headers=headers,
                payload=payload,
                timeout_seconds=45,
            )
            data = resp.json()
            # HF API returns list of entity dicts
            if isinstance(data, list):
                results.append(data)
            else:
                results.append([])
        except Exception as e:
            import logging

            logging.getLogger(__name__).warning(f"HF API NER failed: {e}")
            results.append([])
    return results


_SKILL_ALIAS = {
    "js": "javascript",
    "node": "nodejs",
    "py": "python",
    "ts": "typescript",
}


def canonicalize_skill(s: str) -> str:
    x = (s or "").strip().lower()
    x = re.sub(r"\s+", " ", x)
    return _SKILL_ALIAS.get(x, x)


def parse_entities(text: str) -> dict:
    pipe = load_ner()
    skills: list[str] = []
    orgs: list[str] = []
    names: list[str] = []

    if pipe == "__skipped__":
        ents = []
    elif pipe == "__hf_api__":
        api_results = _ner_via_hf_api([text or ""])
        ents = api_results[0] if api_results else []
    else:
        ents = pipe((text or "")[:30000])

    for e in ents:
        g = e.get("entity_group", "")
        w = (e.get("word") or "").strip()
        if not w:
            continue
        if g in ("MISC", "SKILL"):
            skills.append(w)
        elif g == "ORG":
            orgs.append(w)
        elif g in ("PER", "PERSON"):
            names.append(w)

    # Rule-based skill pickup for common tech tokens (helps when NER labels are generic)
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9+#.]{1,30}", text or "")
    tech = {
        "python",
        "java",
        "golang",
        "go",
        "javascript",
        "typescript",
        "docker",
        "kubernetes",
        "aws",
        "gcp",
        "azure",
        "postgres",
        "postgresql",
        "mysql",
        "redis",
        "fastapi",
        "django",
        "flask",
        "react",
        "node",
        "nodejs",
    }
    for t in tokens:
        tl = t.lower()
        if tl in tech:
            skills.append(t)

    can_skills = sorted({canonicalize_skill(s) for s in skills if s.strip()})
    return {
        "skills": can_skills,
        "orgs": sorted({o.strip() for o in orgs if o.strip()}),
        "names": sorted({n.strip() for n in names if n.strip()}),
        "titles": _extract_titles(text or ""),
        "dates": _extract_dates(text or ""),
        "timeline": _infer_timeline(text or ""),
        "raw_ner": [] if pipe == "__skipped__" else None,
    }


def _extract_dates(text: str) -> list[str]:
    # Very lightweight: capture YYYY or YYYY-MM / YYYY/MM
    years = re.findall(r"\b(?:19\d{2}|20\d{2})(?:[-/](?:0[1-9]|1[0-2]))?\b", text)
    return years


def _extract_titles(text: str) -> list[str]:
    titles = []
    for pat in [r"\bsoftware engineer\b", r"\bengineer\b", r"\bdeveloper\b", r"\bdata scientist\b"]:
        if re.search(pat, text.lower()):
            titles.append(pat.strip("\\b"))
    return sorted(set(titles))


def _infer_timeline(text: str) -> list[dict]:
    # Heuristic: find patterns like "Company - Title (2019-2021)"
    out: list[dict] = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    rng = re.compile(r"(?P<from>19\d{2}|20\d{2})\s*[-–]\s*(?P<to>19\d{2}|20\d{2}|present)", re.IGNORECASE)
    for line in lines[:200]:
        m = rng.search(line)
        if not m:
            continue
        out.append({"company": None, "title": None, "from": str(m.group("from")), "to": str(m.group("to"))})
    return out[:20]
