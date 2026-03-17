import io
import os

from app.config import settings
from huggingface_hub import InferenceClient

# Set Poppler path for Windows
if os.name == 'nt':  # Windows
    poppler_path = r"c:\Users\User\CascadeProjects\cv-analyser-backend\service\poppler-windows\poppler-23.07.0\Library\bin"
    if os.path.exists(poppler_path):
        os.environ['PATH'] = poppler_path + ';' + os.environ.get('PATH', '')


def extract_text_and_layout(file_bytes: bytes, content_type: str) -> tuple[str, dict]:
    """Returns (text, extraction_metadata)."""
    text = ""
    method = "unknown"
    pages = None
    has_scanned_content = False

    if settings.enable_layout_aware_parsing and settings.hf_api_token:
        try:
            if (content_type or "").lower().startswith("image/"):
                text = _extract_via_donut_hf(file_bytes)
                method = "donut_hf"
                pages = 1
                has_scanned_content = True
                text = (text or "").replace("\x00", "")
                return text + "\n", {"method": method, "confidence": None, "pages": pages, "has_scanned_content": has_scanned_content}
        except Exception:
            pass

    if (content_type or "").lower().startswith("image/"):
        import pytesseract
        from PIL import Image

        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        text = pytesseract.image_to_string(img)
        method = "tesseract_ocr"
        pages = 1
        has_scanned_content = True
        text = (text or "").replace("\x00", "")
        return text + "\n", {"method": method, "confidence": None, "pages": pages, "has_scanned_content": has_scanned_content}

    if "pdf" in content_type:
        import pdfplumber

        method = "pdfplumber"
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages = len(pdf.pages)
                page_texts = []
                for page in pdf.pages:
                    ptext = page.extract_text()
                    if ptext:
                        page_texts.append(ptext)
                # Page filtering heuristic: keep pages with resume-like keywords
                if settings.enable_layout_aware_parsing:
                    page_texts = _filter_resume_pages(page_texts)
                text = "\n".join(page_texts)
        except Exception:
            text = ""
        if not text:
            # OCR fallback
            try:
                import pytesseract
                from pdf2image import convert_from_bytes

                imgs = convert_from_bytes(file_bytes)
                pages = len(imgs)

                if settings.enable_layout_aware_parsing and settings.hf_api_token:
                    try:
                        for img in imgs:
                            buf = io.BytesIO()
                            img.save(buf, format="PNG")
                            # Prefer LayoutLMv3 for layout-aware text extraction; fallback to Donut
                            page_text = _extract_via_layoutlmv3_hf(buf.getvalue())
                            if not page_text:
                                page_text = _extract_via_donut_hf(buf.getvalue())
                            text += page_text + "\n"
                        method = "layoutlmv3_hf"
                        has_scanned_content = True
                    except Exception:
                        for page in imgs:
                            text += pytesseract.image_to_string(page) + "\n"
                        method = "tesseract_ocr"
                        has_scanned_content = True
                else:
                    for page in imgs:
                        text += pytesseract.image_to_string(page) + "\n"
                    method = "tesseract_ocr"
                    has_scanned_content = True
            except Exception as ocr_error:
                # If OCR fails, return empty text with error information
                print(f"Warning: OCR fallback failed: {ocr_error}")
                pages = None
                method = "pdfplumber_failed_ocr_failed"
                has_scanned_content = False
        text = (text or "").replace("\x00", "")
        return text, {"method": method, "confidence": None, "pages": pages, "has_scanned_content": has_scanned_content}

    elif "word" in content_type:
        from docx import Document

        method = "python-docx"
        doc = Document(io.BytesIO(file_bytes))
        for p in doc.paragraphs:
            text += p.text + "\n"
        pages = None
        text = (text or "").replace("\x00", "")
        return text, {"method": method, "confidence": None, "pages": pages, "has_scanned_content": has_scanned_content}

    else:
        method = "plain_text"
        text = file_bytes.decode("utf-8", errors="ignore")
        pages = None
        text = (text or "").replace("\x00", "")
        return text, {"method": method, "confidence": None, "pages": pages, "has_scanned_content": has_scanned_content}


def _extract_via_layoutlmv3_hf(image_bytes: bytes) -> str:
    """Extract text with layout awareness using LayoutLMv3 via HF router."""
    try:
        client = InferenceClient(api_key=settings.hf_api_token)
        out = client.document_question_answering(
            image=image_bytes,
            question="Extract all visible text in reading order.",
            model=settings.layoutlmv3_model,
        )
        # Can return dict or list[dict]
        if isinstance(out, list) and out and isinstance(out[0], dict):
            return str(out[0].get("answer") or "")
        if isinstance(out, dict):
            return str(out.get("answer") or "")
        return ""
    except Exception as e:  # noqa: BLE001
        import logging

        logging.getLogger(__name__).warning(f"LayoutLMv3 HF extraction failed: {e}")
        return ""


def _filter_resume_pages(page_texts: list[str]) -> list[str]:
    """Heuristic to keep pages that look like resume content; drop certificate/transcript pages."""
    resume_keywords = {
        "experience", "education", "skills", "projects", "summary", "objective",
        "employment", "work", "career", "qualifications", "certifications", "languages",
        "contact", "phone", "email", "linkedin", "github", "portfolio"
    }
    kept = []
    for txt in page_texts:
        if not txt:
            continue
        lower = txt.lower()
        score = sum(1 for kw in resume_keywords if kw in lower)
        # Keep page if it has several resume keywords or reasonable length and at least one keyword
        if score >= 3 or (score >= 1 and len(lower) > 200):
            kept.append(txt)
        else:
            # Optionally log or count discarded pages
            pass
    return kept


def _extract_via_donut_hf(image_bytes: bytes) -> str:
    try:
        client = InferenceClient(api_key=settings.hf_api_token)
        out = client.image_to_text(image=image_bytes, model=settings.donut_model)
        if isinstance(out, str):
            return out
        if isinstance(out, list) and out and isinstance(out[0], dict):
            return str(out[0].get("generated_text") or out[0].get("text") or "")
        if isinstance(out, dict):
            return str(out.get("generated_text") or out.get("text") or "")
        return ""
    except Exception as e:  # noqa: BLE001
        import logging

        logging.getLogger(__name__).warning(f"Donut HF extraction failed: {e}")
        return ""
