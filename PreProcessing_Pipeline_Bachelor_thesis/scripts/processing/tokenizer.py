import json
from transformers import AutoTokenizer
from scripts.logger.loggerSetup import setup_logger
from pathlib import Path


class TokenHelper:
    def __init__(self, model_name: str = None):
        self.logger = setup_logger(__name__)

        if not model_name:
            config_path = Path(__file__).resolve().parents[2] / "config.json"
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            model_name = config["tokenizer_model"]

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.logger.info(f"Initialized TokenHelper with model '{model_name}'")

    def count_tokens(self, text):
        tokens = self.tokenizer.encode(text)
        self.logger.debug(f"Token count for chunk: {len(tokens)}")
        return len(tokens)
