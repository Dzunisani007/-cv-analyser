from __future__ import annotations

import os
import re
import logging

from app.config import settings
from huggingface_hub import InferenceClient

_ner_pipe = None


def _is_gliner(obj) -> bool:
    try:
        return obj.__class__.__name__.lower() == "gliner"
    except Exception:
        return False


def _ner_via_gliner(pipe, text: str) -> list[dict]:
    labels = ["person", "organization", "skill"]
    out: list[dict] = []
    try:
        preds = pipe.predict_entities(text[:30000], labels)
    except Exception as e:  # noqa: BLE001
        logging.getLogger(__name__).warning(f"GLiNER inference failed: {e}")
        return []

    for p in preds or []:
        if not isinstance(p, dict):
            continue
        label = str(p.get("label") or "").lower()
        txt = str(p.get("text") or "").strip()
        if not txt:
            continue
        if label == "person":
            group = "PER"
        elif label == "organization":
            group = "ORG"
        elif label == "skill":
            group = "SKILL"
        else:
            group = "MISC"
        out.append({"entity_group": group, "word": txt})
    return out


def _use_hf_api() -> bool:
    return bool(settings.hf_api_token)


def load_ner():
    global _ner_pipe
    if _ner_pipe is not None:
        return _ner_pipe

    # Check if we should use lazy loading
    if settings.lazy_model_load:
        # Don't load on startup, will load on first request
        return None
    
    if (os.getenv("SKIP_MODEL_LOAD", "false") or "false").lower() == "true":
        _ner_pipe = "__skipped__"
        return _ner_pipe

    if _use_hf_api():
        _ner_pipe = "__hf_api__"
        return _ner_pipe

    # Try to load from cache first
    from app.model_cache import is_model_cached, mark_model_cached, ensure_cache_dir
    cache_dir = ensure_cache_dir()
    model_cache_path = cache_dir / "ner"
    
    if is_model_cached(settings.ner_model) and model_cache_path.exists():
        try:
            from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline
            tokenizer = AutoTokenizer.from_pretrained(str(model_cache_path))
            model = AutoModelForTokenClassification.from_pretrained(str(model_cache_path))
            _ner_pipe = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
            logger.info(f"Loaded NER model from cache: {model_cache_path}")
            return _ner_pipe
        except Exception as e:
            logger.warning(f"Failed to load NER from cache: {e}")

    # Load from transformers and cache
    from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline
    
    logger.info(f"Loading NER model: {settings.ner_model}")
    tokenizer = AutoTokenizer.from_pretrained(settings.ner_model)
    model = AutoModelForTokenClassification.from_pretrained(settings.ner_model)
    _ner_pipe = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    
    # Cache the model
    try:
        tokenizer.save_pretrained(str(model_cache_path))
        model.save_pretrained(str(model_cache_path))
        mark_model_cached(settings.ner_model, str(model_cache_path))
        logger.info(f"Cached NER model to: {model_cache_path}")
    except Exception as e:
        logger.warning(f"Failed to cache NER model: {e}")
    
    return _ner_pipe


def _ner_via_hf_api(texts: list[str]) -> list[dict]:
    client = InferenceClient(api_key=settings.hf_api_token)
    results: list[list[dict]] = []
    for txt in texts:
        try:
            out = client.token_classification(
                txt or "",
                model=settings.ner_model,
                aggregation_strategy="simple",
            )
            results.append(out if isinstance(out, list) else [])
        except Exception as e:  # noqa: BLE001
            logging.getLogger(__name__).warning(f"HF router NER failed: {e}")
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


def _extract_contacts(text: str) -> dict:
    t = text or ""
    email = None
    phone = None
    linkedin = None
    github = None
    portfolio = None

    m = re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", t, re.IGNORECASE)
    if m:
        email = m.group(0)

    m = re.search(r"\b\+?\d[\d\s().-]{7,}\d\b", t)
    if m:
        phone = re.sub(r"\s+", " ", m.group(0)).strip()

    m = re.search(r"https?://(?:www\.)?linkedin\.com/[^\s)>,]+", t, re.IGNORECASE)
    if m:
        linkedin = m.group(0).rstrip(".,;")
    else:
        m = re.search(r"\blinkedin\.com/[^\s)>,]+", t, re.IGNORECASE)
        if m:
            linkedin = "https://" + m.group(0).rstrip(".,;")

    m = re.search(r"https?://(?:www\.)?github\.com/[^\s)>,]+", t, re.IGNORECASE)
    if m:
        github = m.group(0).rstrip(".,;")
    else:
        m = re.search(r"\bgithub\.com/[^\s)>,]+", t, re.IGNORECASE)
        if m:
            github = "https://" + m.group(0).rstrip(".,;")

    m = re.search(r"https?://[^\s)>,]+", t, re.IGNORECASE)
    if m:
        url = m.group(0).rstrip(".,;")
        if linkedin and url == linkedin:
            pass
        elif github and url == github:
            pass
        else:
            portfolio = url

    return {
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "portfolio": portfolio,
    }


def _guess_full_name(text: str, names: list[str]) -> str | None:
    if names:
        cand = sorted(names, key=lambda s: len(s), reverse=True)[0].strip()
        if len(cand.split()) >= 2:
            return cand

    lines = [l.strip() for l in (text or "").splitlines() if l.strip()]
    for line in lines[:5]:
        if "@" in line or "http" in line.lower():
            continue
        if len(line) > 60:
            continue
        if re.search(r"\d", line):
            continue
        if len(line.split()) in (2, 3, 4):
            return line
    return None


def _extract_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"experience": [], "education": [], "skills": [], "summary": []}
    current = None
    lines = [l.rstrip() for l in (text or "").splitlines()]
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        low = re.sub(r"\s+", " ", line).lower().strip(":")

        if low in {"experience", "work experience", "professional experience", "employment history", "career"}:
            current = "experience"
            continue
        if low in {"education", "academic", "academics"}:
            current = "education"
            continue
        if low in {"skills", "technical skills", "core skills", "technologies", "tools"}:
            current = "skills"
            continue
        if low in {"summary", "professional summary", "profile", "about", "objective"}:
            current = "summary"
            continue

        if current:
            sections[current].append(line)

    return sections


def _extract_education(text: str, section_lines: list[str]) -> tuple[list[dict], list[str], list[str]]:
    degrees = []
    certifications: list[str] = []
    languages: list[str] = []

    t = text or ""
    edu_text = "\n".join(section_lines) if section_lines else t

    degree_pat = re.compile(
        r"\b(phd|doctorate|master|msc|m\.sc|mba|bachelor|bsc|b\.sc|ba|bs)\b",
        re.IGNORECASE,
    )
    school_pat = re.compile(r"\b(university|college|institute|polytechnic)\b", re.IGNORECASE)

    for line in [l.strip() for l in edu_text.splitlines() if l.strip()][:80]:
        if degree_pat.search(line) or school_pat.search(line):
            years = re.findall(r"\b(?:19\d{2}|20\d{2})\b", line)
            degrees.append(
                {
                    "institution": None,
                    "degree": line,
                    "field": None,
                    "from": years[0] if years else None,
                    "to": years[-1] if len(years) >= 2 else (years[0] if years else None),
                }
            )

    for m in re.finditer(r"\b(aws certified|pmp|cissp|ccna|azure fundamentals|google cloud|scrum master)\b", t, re.IGNORECASE):
        certifications.append(m.group(0))

    for m in re.finditer(r"\b(english|french|arabic|spanish|german|italian|portuguese|hindi|urdu)\b", t, re.IGNORECASE):
        languages.append(m.group(0))

    certifications = sorted({c.strip() for c in certifications if c.strip()})
    languages = sorted({l.strip() for l in languages if l.strip()})
    return degrees[:30], certifications[:50], languages[:50]


def _extract_experience(text: str, section_lines: list[str]) -> list[dict]:
    exp_text = "\n".join(section_lines) if section_lines else (text or "")
    lines = [l.strip() for l in exp_text.splitlines() if l.strip()]
    out: list[dict] = []
    rng = re.compile(r"(?P<from>19\d{2}|20\d{2})\s*[-–]\s*(?P<to>19\d{2}|20\d{2}|present)", re.IGNORECASE)

    for line in lines[:160]:
        m = rng.search(line)
        if m:
            out.append(
                {
                    "company": None,
                    "title": None,
                    "from": str(m.group("from")),
                    "to": str(m.group("to")),
                    "description": line,
                }
            )

    if not out and lines:
        blob = " ".join(lines[:40])
        if len(blob.split()) >= 10:
            out.append({"company": None, "title": None, "from": None, "to": None, "description": blob})

    return out[:40]


def parse_entities(text: str) -> dict:
    pipe = get_ner_model()
    skills: list[str] = []
    orgs: list[str] = []
    names: list[str] = []

    if pipe == "__skipped__":
        ents = []
    elif pipe == "__hf_api__":
        api_results = _ner_via_hf_api([text or ""])
        ents = api_results[0] if api_results else []
    elif _is_gliner(pipe):
        ents = _ner_via_gliner(pipe, text or "")
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
    sections = _extract_sections(text or "")
    contacts = _extract_contacts(text or "")
    full_name = _guess_full_name(text or "", names)
    education, certifications, languages = _extract_education(text or "", sections.get("education") or [])
    experience = _extract_experience(text or "", sections.get("experience") or [])

    position = None
    if sections.get("summary"):
        position = " ".join(sections.get("summary")[:2]).strip() or None

    return {
        "skills": can_skills,
        "orgs": sorted({o.strip() for o in orgs if o.strip()}),
        "names": sorted({n.strip() for n in names if n.strip()}),
        "titles": _extract_titles(text or ""),
        "dates": _extract_dates(text or ""),
        "timeline": _infer_timeline(text or ""),
        "personal_details": {
            "full_name": full_name,
            "email": contacts.get("email"),
            "phone": contacts.get("phone"),
            "address": None,
            "dob": None,
            "linkedin": contacts.get("linkedin"),
            "github": contacts.get("github"),
            "portfolio": contacts.get("portfolio"),
        },
        "education_details": {
            "education": education,
            "certifications": certifications,
            "languages": languages,
        },
        "professional_details": {
            "skills": can_skills,
            "experience": experience,
            "position": position,
            "previous_companies": sorted({o.strip() for o in orgs if o.strip()}),
            "bio": "\n".join((sections.get("summary") or [])[:8]).strip() if sections.get("summary") else "",
        },
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
