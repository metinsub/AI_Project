import datetime
import json
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

from scripts.extractor import extract_sections
from scripts.processing.chunker import chunk_sections
from scripts.evaluation.eval_output import rephrase_with_evaluation
from scripts.exporter import export_to_pdf
from scripts.logger.loggerSetup import setup_logger

logger = setup_logger(__name__)


def run_pipeline(input_pdf_path: str) -> None:
    pdf_path = Path(input_pdf_path)
    base_name = pdf_path.stem

    config_path = Path("config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        output_dir = Path("data/output")
        log_dir = Path("logs")
        output_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)

        rephrase_pdf_path = output_dir / f"{base_name}_Rephrased_{timestamp}.pdf"
        error_log_file = log_dir / f"{base_name}_failed_chunks__{timestamp}.json"

        sections = extract_sections(
            str(pdf_path), base_name=base_name, timestamp=timestamp
        )
        if not sections:
            raise ValueError("No sections extracted.")

        logger.info("Chunking sections...")
        chunks = chunk_sections(
            sections, config, chunk_overlap=config["chunk_overlap"]
        )

        logger.info("Rephrasing chunks...")
        errors = {}

        def process(chunk):
            header = chunk["metadata"].get("header", "Unknown Header")
            chunk_id = chunk["metadata"].get("chunk_id", "unknown_chunk")
            logger.info(f"Processing: Header='{header}' | Chunk ID='{chunk_id}'")
            try:
                return rephrase_with_evaluation(chunk)
            except Exception as e:
                logger.warning(f"Chunk '{header}' failed rephrasing: {e}")
                errors[header] = str(e)
                return {
                    "metadata": chunk["metadata"],
                    "page_content": chunk["page_content"]
                }

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(tqdm(executor.map(process, chunks), total=len(chunks)))

        rephrase_map = defaultdict(list)
        for chunk in results:
            header = chunk["metadata"].get("header", "")
            rephrase_map[header].append(chunk["page_content"])

        combined = [
            {
                "header": section["header"],
                "rephrased": "\n".join(
                    rephrase_map.get(
                        section["header"], ["No rephrased text available."]
                    )
                )
            }
            for section in sections
        ]

        export_to_pdf(combined, rephrase_pdf_path)

        if errors:
            with open(error_log_file, "w", encoding="utf-8") as f:
                json.dump(errors, f, indent=2, ensure_ascii=False)

        logger.info(
            f"Pipeline completed. Processed {len(results)} chunks across "
            f"{len(sections)} headers."
        )
