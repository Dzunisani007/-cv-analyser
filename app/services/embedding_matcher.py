from __future__ import annotations

import os
import numpy as np
import requests

from app.config import settings

_model = None


def _use_hf_api() -> bool:
    return bool(settings.hf_api_token)


def load_embed():
    global _model
    if _model is not None:
        return _model

    if (os.getenv("SKIP_MODEL_LOAD", "false") or "false").lower() == "true":
        _model = "__skipped__"
        return _model

    if _use_hf_api():
        _model = "__hf_api__"
        return _model

    from sentence_transformers import SentenceTransformer

    _model = SentenceTransformer(settings.embed_model)
    return _model


def embed_text(texts: list[str]) -> np.ndarray:
    m = load_embed()
    if m == "__skipped__":
        # Return zero embeddings in SKIP_MODEL_LOAD mode
        return np.zeros((len(texts), 384))
    if m == "__hf_api__":
        return _embed_via_hf_api(texts)
    # Local model
    return m.encode(texts, convert_to_numpy=True, show_progress_bar=False)


def match_skills_to_job(extracted_skills: list[str], job_description: str | None, threshold: float = 0.7) -> list[dict]:
    if not extracted_skills:
        return []
    if not job_description:
        return [{"skill": s, "score": None} for s in extracted_skills]

    job_emb = embed_text([job_description])[0]
    skill_embs = embed_text(extracted_skills)

    results: list[dict] = []
    try:
        import numpy as np  # type: ignore

        for skill, emb in zip(extracted_skills, skill_embs):
            denom = float(np.linalg.norm(emb) * np.linalg.norm(job_emb) + 1e-8)
            cos = float(np.dot(emb, job_emb) / denom) if denom else 0.0
            results.append({"skill": skill, "score": cos})
    except Exception:
        # Fallback: if numpy isn't available, return null scores.
        for skill in extracted_skills:
            results.append({"skill": skill, "score": None})
    return results


def extract_required_skills_from_job(job_description: str | None) -> list[str]:
    if not job_description:
        return []
    # Lightweight heuristic: treat capitalized tokens and common tech tokens as candidates.
    tokens = [t.strip(" ,.;:()[]{}\n\t").lower() for t in job_description.split()]
    stop = {"and", "or", "with", "the", "a", "an", "to", "in", "of", "for"}
    cand = [t for t in tokens if t and t not in stop and len(t) <= 24]
    # Deduplicate while preserving order.
    seen = set()
    out = []
    for t in cand:
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out[:40]
