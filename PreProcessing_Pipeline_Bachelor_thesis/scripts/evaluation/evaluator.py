"""
Handles the evaluation of rephrased text against an original text using an LLM.

This module loads evaluation configuration, model parameters, and prompt templates
to interact with an Ollama API endpoint for generating evaluations based on
predefined metrics. It validates the LLM's response against a JSON schema.
"""

import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from pydantic import ValidationError

from .parsed_evaluator import EvaluatorResult
from scripts.logger.loggerSetup import setup_logger

load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_API_URL")

base_dir = Path(__file__).resolve().parent
config_path = base_dir / "eval_config.json"


with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

model_name = config.get("model_name")
temperature = config.get("temperature")
max_tokens = config.get("max_tokens")


project_root = base_dir.parent.parent 
prompt_path = project_root / "prompts" / "evaluator_prompt.txt"


_raw_prompt = prompt_path.read_text(encoding="utf-8")

_escaped = _raw_prompt.replace("{", "{{").replace("}", "}}")
for placeholder in ("metric_descriptions", "input_text", "rephrased_text"):
    _escaped = _escaped.replace(f"{{{{{placeholder}}}}}", f"{{{placeholder}}}")

BASE_EVALUATOR_PROMPT = _escaped

schema_path = base_dir / "evaluator_schema.json"
with open(schema_path, "r", encoding="utf-8") as f:
    EVALUATOR_SCHEMA = json.load(f)

logger = setup_logger(__name__)

class Evaluator:
    """
    Orchestrates the evaluation of text.

    This class loads metrics, builds prompts, interacts with Ollama,
    parses and validates the LLM's response, and checks results against
    predefined thresholds.
    """
    def __init__(self, metrics_file_path: str):
        """
        Initializes the Evaluator with metrics from the specified file.

        Args:
            metrics_file_path: Path to the JSON file containing evaluation metrics.
        """
        self.metrics = self._load_metrics(metrics_file_path)

    def _load_metrics(self, path: str) -> list[dict]:
        """
        Loads evaluation metrics from a JSON file.

        Args:
            path: The path to the metrics JSON file.

        Returns:
            A list of metric dictionaries.

        Raises:
            FileNotFoundError: If the metrics file is not found.
            ValueError: If the metrics file is improperly formatted.
        """
        file_path_obj = Path(path)
        try:
            data = json.loads(file_path_obj.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON from {path}: {e}") from e

        if "metrics" not in data or not isinstance(data["metrics"], list):
            raise ValueError(
                f"{path} must contain a top‐level 'metrics' field as a list"
            )
        return data["metrics"]

    def _build_prompt(self, input_text: str, rephrased_text: str) -> str:
        """
        Assembles the evaluation prompt using the base template and current texts.

        Args:
            input_text: The original input text.
            rephrased_text: The rephrased text to be evaluated.

        Returns:
            The fully constructed prompt string.
        """
        desc_lines = [
            f"- {m['name'].capitalize()}: {m['description']}"
            for m in self.metrics
        ]
        metric_descriptions = "\n".join(desc_lines)
        return BASE_EVALUATOR_PROMPT.format(
            metric_descriptions=metric_descriptions,
            input_text=input_text,
            rephrased_text=rephrased_text
        )

    def _send_ollama_request(self, prompt: str) -> dict:
        """
        Sends a request to Ollama and returns the parsed JSON response.

        Args:
            prompt: The prompt to send.

        Returns:
            The JSON response.

        Raises:
            requests.exceptions.RequestException: If the API request fails.
            ValueError: If the API response cannot be decoded as JSON.
        """
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json", 
            "options": {
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        }
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=120)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {e}")
            raise

        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            logger.error(
                f"Failed to parse Ollama API response as JSON: '{response.text}'. "
                f"Error: {e}"
            )
            raise ValueError(
                f"Failed to parse Ollama API response as JSON: {e}"
            ) from e

    def _process_ollama_response(self, response_json: dict) -> EvaluatorResult:
        """
        Processes the response, parsing and validating the evaluation data.

        Args:
            response_json: The parsed JSON response from Ollama.

        Returns:
            An EvaluatorResult object containing the validated evaluation.

        Raises:
            ValueError: If the response format is invalid or validation fails.
        """
        raw_eval_json_str = response_json.get("response")
        if raw_eval_json_str is None:
            logger.error(
                "Ollama response missing 'response' field or field is null: "
                f"{response_json}"
            )
            raise ValueError(
                "Ollama response missing 'response' field or field is null."
            )

        try:
            parsed_eval_data = json.loads(raw_eval_json_str)
        except json.JSONDecodeError as e:
            logger.error(
                f"Invalid JSON in Ollama 'response' field: '{raw_eval_json_str}'. "
                f"Error: {e}"
            )
            raise ValueError(
                f"Invalid JSON in Ollama 'response' field: {e}\n"
                f">>> {raw_eval_json_str}"
            ) from e

        try:
            validated_result = EvaluatorResult(**parsed_eval_data)
            return validated_result
        except ValidationError as ve:
            error_items = [
                f"{'.'.join(map(str, err['loc']))}: {err['msg']}"
                for err in ve.errors()
            ]
            error_detail_str = "; ".join(error_items)
            logger.error(
                f"Pydantic validation failed for evaluation data: {error_detail_str}\n"
                f">>> {parsed_eval_data}"
            )
            raise ValueError(
                f"Pydantic validation failed: {error_detail_str}"
            ) from ve

    def evaluate(self, input_text: str, rephrased_text: str) -> dict:
        """
        Evaluates rephrased text against input text using an LLM via Ollama.

        Args:
            input_text: The original text.
            rephrased_text: The rephrased text to be evaluated.

        Returns:
            A dictionary containing validated evaluation scores and reasoning.
        """
        prompt = self._build_prompt(input_text, rephrased_text)
        api_response_json = self._send_ollama_request(prompt)
        validated_result = self._process_ollama_response(api_response_json)
        return validated_result.dict()

    def check_thresholds(self, evaluation_result: dict) -> tuple[bool, str]:
        """
        Checks if all metric scores in the evaluation result meet their thresholds.

        Args:
            evaluation_result: A dictionary containing evaluation scores, typically
                               from `EvaluatorResult.dict()`.

        Returns:
            A tuple containing:
                - bool: True if all metrics meet thresholds, False otherwise.
                - str: A message indicating the outcome.
        """
        for metric in self.metrics:
            metric_name = metric["name"]
            threshold = metric.get("threshold", 0.0)
            
            # Ensure 'scores' exists and is a dictionary
            scores_dict = evaluation_result.get("scores")
            if not isinstance(scores_dict, dict):
                msg = (
                    f"Evaluation result missing 'scores' dictionary or it's not a dict. "
                    f"Cannot check threshold for '{metric_name}'."
                )
                logger.warning(msg)
                return False, msg

            score = scores_dict.get(metric_name, 0.0)
            
            if not isinstance(score, (int, float)):
                msg = (
                    f"Score for metric '{metric_name}' is not a number: {score}. "
                    f"Cannot compare with threshold {threshold}."
                )
                logger.warning(msg)
                return False, msg

            if score < threshold:
                msg = (
                    f"Metric '{metric_name}' score {score} "
                    f"is below threshold {threshold}."
                )
                logger.warning(msg)
                return False, msg

        logger.info("All metrics meet the required thresholds.")
        return True, "All metrics meet the required thresholds."
