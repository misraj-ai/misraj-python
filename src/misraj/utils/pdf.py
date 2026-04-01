import fitz
from concurrent.futures import ThreadPoolExecutor
from typing import Union, List
from pathlib import Path


def render_page(page_index: int, doc_path_or_bytes: Union[str, bytes], matrix: fitz.Matrix) -> bytes:
    """Helper function to render a single page in a separate thread."""
    # We open the doc inside the worker to ensure thread safety
    if isinstance(doc_path_or_bytes, bytes):
        doc = fitz.open("pdf", doc_path_or_bytes)
    else:
        doc = fitz.open(doc_path_or_bytes)

    page = doc.load_page(page_index)
    # colorspace="rgb" and alpha=False significantly speed up rendering
    pix = page.get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=False)
    img_bytes = pix.tobytes("png")

    doc.close()
    return img_bytes


def convert_pdf_to_images(pdf_content: Union[bytes, str], zoom: int = 4) -> List[bytes]:
    """
    Optimized conversion using parallel processing and optimized rendering settings.
    """
    matrix = fitz.Matrix(zoom, zoom)

    # We open once just to get the page count
    if isinstance(pdf_content, str):
        with fitz.open(pdf_content) as doc:
            page_count = doc.page_count
    else:
        with fitz.open("pdf", pdf_content) as doc:
            page_count = doc.page_count

    # Parallelize the rendering of pages
    # Note: Use max_workers based on your CPU cores
    with ThreadPoolExecutor() as executor:
        # Pass pdf_content to each worker
        results = executor.map(
            lambda i: render_page(i, pdf_content, matrix),
            range(page_count)
        )

    return list(results)
