def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF on disk using PyMuPDF (imported lazily)."""
    import fitz  # PyMuPDF

    text = ""

    document = fitz.open(pdf_path)

    for page in document:
        text += page.get_text()

    document.close()

    return text