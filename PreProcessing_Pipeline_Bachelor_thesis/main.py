import argparse
from scripts.pipeline import run_pipeline
from scripts.logger.loggerSetup import setup_logger


logger = setup_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="RAG Pipeline Runner")
    parser.add_argument(
        "--input", required=True,
        help="Path to input PDF, e.g. 'data/input/PAK-Confluence.pdf'"
    )
    return parser.parse_args()


def main():
    """Run the RAG Pipeline with given input PDF."""
    args = parse_args()
    try:
        run_pipeline(args.input)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()
