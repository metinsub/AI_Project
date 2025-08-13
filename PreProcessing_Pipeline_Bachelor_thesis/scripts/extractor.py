import json
import fitz  # PyMuPDF
import numpy as np
from pathlib import Path
from scripts.logger.loggerSetup import setup_logger

logger = setup_logger(__name__)


def analyze_fonts(doc):
    """Analyze fonts to detect main header styles."""
    font_sizes = [
        span["size"]
        for page in doc
        for block in page.get_text("dict")["blocks"]
        if block["type"] == 0
        for line in block["lines"]
        for span in line["spans"]
    ]
    if not font_sizes:
        return {"median": 0, "main_header_sizes": []}

    median = np.median(font_sizes)
    headers = sorted(
        {size for size in font_sizes if size > median * 1.2}, reverse=True
    )[:2]
    logger.info(f"Detected header font sizes: {headers}")
    return {"median": median, "main_header_sizes": headers}


def extract_blocks(doc, font_stats):
    """Extract text blocks with format info and header detection."""
    blocks = []
    for page_num, page in enumerate(doc):
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0:
                continue  # Skip non-text blocks

            text = []
            sizes = []
            is_bold = False
            for line in block["lines"]:
                for span in line["spans"]:
                    text.append(span["text"])
                    sizes.append(span["size"])
                    is_bold = is_bold or "bold" in span["font"].lower()

            block_text = " ".join(text).strip()
            if not block_text:
                continue

            avg_size = np.mean(sizes) if sizes else 0
            is_header = (
                avg_size in font_stats["main_header_sizes"] and
                is_bold and len(block_text.split()) <= 15
            )

            blocks.append({
                "text": block_text,
                "is_main_header": is_header,
                "page": page_num + 1,
                "index": len(blocks)
            })
    return blocks


def process_sections(blocks):
    """Organize blocks into sections based on headers."""
    headers = [b for b in blocks if b["is_main_header"]]
    if not headers:
        logger.warning(
            "No headers detected — entire document will be one section."
        )

    sections = []
    for i, header in enumerate(headers):
        start = header["index"] + 1
        end = headers[i + 1]["index"] if i + 1 < len(headers) else len(blocks)
        content = " ".join(blocks[j]["text"] for j in range(start, end))

        sections.append({
            "header": header["text"],
            "text": content,
            "original_index": header["index"],
            "page": header["page"]
        })
    return sections


def extract_sections(
    pdf_path: str, base_name: str = None, timestamp: str = None
):
    """Extract structured sections from a PDF."""
    logger.info("Extracting content from PDF...")

    doc = fitz.open(pdf_path)
    try:
        font_stats = analyze_fonts(doc)
        blocks = extract_blocks(doc, font_stats)
        sections = process_sections(blocks)
    finally:
        doc.close()

    logger.info(f"Extracted {len(sections)} sections.")

    if base_name and timestamp:
        output_path = (
            Path("data/extracted") / f"{base_name}_raw_sections_{timestamp}.json"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved raw sections to {output_path}")

    return sections
