import io
import httpx
import pdfplumber


def extract_pdf_text(source: str, max_chars: int = 20000) -> str:
    """Extract text from a PDF given a file path or HTTP URL."""
    if source.startswith("http://") or source.startswith("https://"):
        response = httpx.get(source, follow_redirects=True, timeout=30)
        response.raise_for_status()
        pdf_file = io.BytesIO(response.content)
    else:
        pdf_file = open(source, "rb")

    try:
        with pdfplumber.open(pdf_file) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n\n".join(pages).strip()[:max_chars]
    finally:
        if hasattr(pdf_file, "close"):
            pdf_file.close()
