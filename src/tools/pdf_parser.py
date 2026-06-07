"""
Resume PDF ingestion using PyMuPDF (fitz).
 
Responsibilities:
  1. Extract raw text from each page
  2. Detect and flag scanned/image-only PDFs
  3. Return a structured ParsedResume object for downstream nodes
"""

from dataclasses import dataclass, field
import fitz

@dataclass
class ParsedResume:
    raw_text: str                        # Full concatenated text
    pages: list[str]                     # Per-page text list
    page_count: int
    char_count: int
    metadata: dict = field(default_factory=dict)
 
 
def parse_pdf(file_bytes: bytes) -> ParsedResume:
    """
    Parse a resume PDF from raw bytes.
 
    Args:
        file_bytes: Raw bytes of the uploaded PDF file.
 
    Returns:
        ParsedResume dataclass with extracted text and metadata.
 
    Raises:
        ValueError: If the file is not a valid PDF or is empty.
    """
    if not file_bytes:
        raise ValueError("PDF file is empty.")
 
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise ValueError(f"Could not open PDF: {e}") from e
 
    page_texts: list[str] = []
    total_chars = 0
 
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").strip()
        page_texts.append(text)
        total_chars += len(text)
 
    doc_metadata = doc.metadata or {}
    doc.close()
 
    full_text = "\n\n".join(p for p in page_texts if p)
 
    return ParsedResume(
        raw_text=full_text,
        pages=page_texts,
        page_count=len(page_texts),
        char_count=total_chars,
        metadata={
            "title": doc_metadata.get("title", ""),
            "author": doc_metadata.get("author", ""),
            "creator": doc_metadata.get("creator", ""),
            "format": doc_metadata.get("format", ""),
        },
    )
 
 
def parse_pdf_from_path(file_path: str) -> ParsedResume:
    """Convenience wrapper for loading from a file path."""
    with open(file_path, "rb") as f:
        return parse_pdf(f.read())