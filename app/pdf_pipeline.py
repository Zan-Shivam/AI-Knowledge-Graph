from app.llm_extractor import extract_with_llm
from app.graph_merge import merge_graphs
from app.chunker import chunk_text
from concurrent.futures import ThreadPoolExecutor

def _process_single_page(page):
    chunks = chunk_text(page["text"])
    page_results = []

    for chunk in chunks:
        result = extract_with_llm(chunk)
        page_results.append(result)

    return merge_graphs(page_results)


def process_pdf_pages(pages):
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(_process_single_page, pages))

    return merge_graphs(results)
