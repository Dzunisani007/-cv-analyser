import io


def extract_text_and_layout(file_bytes: bytes, content_type: str) -> tuple[str, dict]:
    """Returns (text, extraction_metadata)."""
    text = ""
    method = "unknown"
    pages = None
    has_scanned_content = False

    if (content_type or "").lower().startswith("image/"):
        import pytesseract
        from PIL import Image

        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        text = pytesseract.image_to_string(img)
        method = "tesseract_ocr"
        pages = 1
        has_scanned_content = True
        return text + "\n", {"method": method, "confidence": None, "pages": pages, "has_scanned_content": has_scanned_content}

    if "pdf" in content_type:
        import pdfplumber

        method = "pdfplumber"
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages = len(pdf.pages)
                for page in pdf.pages:
                    ptext = page.extract_text()
                    if ptext:
                        text += ptext + "\n"
        except Exception:
            text = ""
        if not text:
            # OCR fallback
            import pytesseract
            from pdf2image import convert_from_bytes

            pages = len(convert_from_bytes(file_bytes))
            for page in convert_from_bytes(file_bytes):
                text += pytesseract.image_to_string(page) + "\n"
            method = "tesseract_ocr"
            has_scanned_content = True
        return text, {"method": method, "confidence": None, "pages": pages, "has_scanned_content": has_scanned_content}

    elif "word" in content_type:
        from docx import Document

        method = "python-docx"
        doc = Document(io.BytesIO(file_bytes))
        for p in doc.paragraphs:
            text += p.text + "\n"
        pages = None
        return text, {"method": method, "confidence": None, "pages": pages, "has_scanned_content": has_scanned_content}

    else:
        method = "plain_text"
        text = file_bytes.decode("utf-8", errors="ignore")
        pages = None
        return text, {"method": method, "confidence": None, "pages": pages, "has_scanned_content": has_scanned_content}
