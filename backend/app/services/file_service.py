"""Utilities for working with PDF/Word documents stored on QNAP."""

import os


def get_preview_pdf(file_path: str, max_pages: int = 2) -> bytes | None:
    """Extract the first *max_pages* pages from a PDF and return the result as
    bytes of a new PDF.  Returns ``None`` on error.

    Uses PyMuPDF (``fitz``) which handles most real-world PDFs well.
    """
    try:
        import fitz  # PyMuPDF

        src = fitz.open(file_path)
        dst = fitz.open()  # empty document

        pages_to_copy = min(max_pages, len(src))
        dst.insert_pdf(src, from_page=0, to_page=pages_to_copy - 1)

        pdf_bytes = dst.tobytes()
        dst.close()
        src.close()
        return pdf_bytes
    except Exception as e:
        print(f"Error creating preview for {file_path}: {e}")
        return None


def get_page_count(file_path: str) -> int | None:
    """Return the number of pages in a PDF, or None on error."""
    try:
        import fitz

        doc = fitz.open(file_path)
        count = len(doc)
        doc.close()
        return count
    except Exception:
        return None


def allowed_file(filename: str) -> bool:
    """Check whether the file extension is one we accept."""
    allowed = {"pdf", "doc", "docx"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def safe_filename(filename: str) -> str:
    """Sanitise a user-supplied filename into something safe for storage."""
    from werkzeug.utils import secure_filename as _sf

    return _sf(filename) or "document"
