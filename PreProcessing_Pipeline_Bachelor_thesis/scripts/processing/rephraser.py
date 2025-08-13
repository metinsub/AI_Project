import os
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv
from requests.exceptions import RequestException
from scripts.logger.loggerSetup import setup_logger

# Load environment variables
load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_API_URL")

# Load model_name and generation parameters from config.json
config_path = Path(__file__).resolve().parents[2] / "config.json"
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

model_name = config["model_name"]
temperature = config.get("temperature", 0.1)
max_tokens = config.get("max_tokens", 2000)

# Load the rephrase and feedback prompts from files
PROMPT_DIR = Path(__file__).resolve().parents[2] / "prompts"
with open(PROMPT_DIR / "rephraser_prompt.txt", "r", encoding="utf-8") as f:
    BASE_PROMPT = f.read()
with open(PROMPT_DIR / "feedback_prompt.txt", "r", encoding="utf-8") as f:
    FEEDBACK_PROMPT = f.read()

logger = setup_logger(__name__)


def rephrase_chunk(
    chunk, feedback=None, previous_rephrased_text=None, original_text=None, retries=2
):
    header = chunk["metadata"].get("header", "")
    text = chunk.get("page_content", "")

    input_text = original_text if original_text else text

    if feedback and previous_rephrased_text:
        prompt = FEEDBACK_PROMPT.format(
            header=header,
            input_text=input_text,
            previous_rephrased_text=previous_rephrased_text,
            feedback=feedback
        )
    else:
        prompt = BASE_PROMPT.format(
            header=header,
            input_text=input_text
        )

    for count in range(retries + 1):
        attempts = count + 1
        try:
            logger.info(f"Rephrasing chunk: '{header}' (Attempt {attempts})")
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            response_data = response.json()
            return {
                "metadata": chunk["metadata"],
                "page_content": response_data["response"].strip()
            }
        except RequestException as e:
            logger.warning(
                f"Request failed for chunk '{header}' on attempt {attempts}: {e}"
            )
            if count == retries:
                logger.error(
                    f"All {retries + 1} attempts failed for chunk '{header}'. "
                    f"Raising exception."
                )
                raise
            time.sleep(120)
