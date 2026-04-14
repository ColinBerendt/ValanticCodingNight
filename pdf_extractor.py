import pdfplumber


def extract_text(pdf_path: str) -> str:
    """Extract all text content from a PDF file."""
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n\n".join(pages)
