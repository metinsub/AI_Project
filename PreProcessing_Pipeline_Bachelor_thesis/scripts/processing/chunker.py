from langchain.text_splitter import RecursiveCharacterTextSplitter
from scripts.processing.tokenizer import TokenHelper


def chunk_sections(sections, config, chunk_overlap):
    """Split sections into smaller chunks based on token limits."""
    tokenizer = TokenHelper(config["tokenizer_model"])
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["chunk_size"],
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n", "\n", ". ", "? ", "! ", "; ", ": ", " - ", ", ", " "
        ]
    )
    max_tokens = config["max_tokens_check"]

    chunks = []
    for section in sections:
        header = section.get("header", "").strip()
        text = section.get("text", "").strip()

        if not text:
            continue  # Skip empty sections

        tokens = tokenizer.count_tokens(text)

        if tokens <= max_tokens:
            chunks.append(make_chunk(text, header, 0, tokens))
            continue

        for i, part in enumerate(splitter.split_text(text)):
            part = part.strip()
            if not part:
                continue
            part_tokens = tokenizer.count_tokens(part)
            if part_tokens <= max_tokens:
                chunks.append(make_chunk(part, header, i, part_tokens))

    return chunks


def make_chunk(text, header, idx, tokens):
    """Helper to create a chunk dict."""
    return {
        "page_content": text,
        "metadata": {
            "header": header,
            "chunk_id": f"{header.replace(' ', '_')}_{idx}",
            "token_count": tokens
        }
    }
