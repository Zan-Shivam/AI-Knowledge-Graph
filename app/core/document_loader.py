from pypdf import PdfReader

def extract_pages_from_pdf(file_path: str):
    reader = PdfReader(file_path)
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append({
                "page": i + 1,
                "text": text
            })

    return pages
