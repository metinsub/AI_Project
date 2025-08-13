import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv

from scripts.evaluation.evaluator import Evaluator
from scripts.logger.loggerSetup import setup_logger
from scripts.processing.rephraser import rephrase_chunk


project_root = Path(__file__).resolve().parents[2]
os.environ.setdefault('PYTHONPATH', str(project_root))

# Load environment variables
load_dotenv(project_root / '.env')
OLLAMA_URL = os.getenv('OLLAMA_API_URL')
if not OLLAMA_URL:
    raise RuntimeError(
        'OLLAMA_API_URL is not set in .env'
    )

# Load model parameters (used by Evaluator via its global scope)
config_file = project_root / 'scripts' / 'evaluation' / 'eval_config.json'
with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

MODEL_NAME = config.get('model_name') # Used by Evaluator
TEMPERATURE = config.get('temperature') # Used by Evaluator
MAX_TOKENS = config.get('max_tokens') # Used by Evaluator

metrics_file_path = project_root / 'scripts' / 'evaluation' / 'metrics.json'

# Initialize logger and evaluator
logger = setup_logger(__name__)
evaluator = Evaluator(metrics_file_path=str(metrics_file_path))



def rephrase_with_evaluation(chunk_data: dict, max_attempts: int = 5) -> dict:
    """
    Repeatedly rephrase 'chunk_data' and evaluate it until it passes all metrics
    or until max_attempts is reached. Returns the best rephrased chunk.
    """
    chunk_header = chunk_data['metadata'].get('header', 'Unknown Header')
    original_text = chunk_data.get('page_content', '')

    best_rephrase_obj = None
    best_score_sum = -1.0
    last_feedback = None
    prev_rephrase_text = None

    for attempt in range(1, max_attempts + 1):
        rephrased_obj = rephrase_chunk(
            chunk_data,
            feedback=last_feedback,
            previous_rephrased_text=prev_rephrase_text,
            original_text=original_text 
        )
        rephrased_text = rephrased_obj['page_content']

        try:
            evaluation_result = evaluator.evaluate(original_text, rephrased_text)
        except Exception as eval_error:
            logger.warning(
                "Chunk '%s' evaluation failed on attempt %d: %s",
                chunk_header, attempt, eval_error
            )
            if attempt == max_attempts:
                logger.error(
                    "Chunk '%s' evaluation failed on final attempt. Raising error.",
                    chunk_header
                )
                raise
            last_feedback = f'Evaluation error: {eval_error}' 
            prev_rephrase_text = rephrased_text
            time.sleep(3) 
            continue

        logger.info(
            "Evaluation for chunk '%s', attempt %d: %s",
            chunk_header, attempt, evaluation_result
        )

        passed, message = evaluator.check_thresholds(evaluation_result)
                
        current_score_sum = sum(evaluation_result.get('scores', {}).values())

        if current_score_sum > best_score_sum:
            best_score_sum = current_score_sum
            best_rephrase_obj = rephrased_obj
            logger.info(
                "Chunk '%s', attempt %d is new best with score sum: %.2f",
                chunk_header, attempt, best_score_sum
            )

        if passed:
            logger.info(
                "Chunk '%s' accepted on attempt %d. Scores: %s",
                chunk_header, attempt, evaluation_result.get('scores')
            )
            return rephrased_obj # Return the successfully evaluated rephrased object


        feedback_from_eval = evaluation_result.get('feedback', '')
        last_feedback = feedback_from_eval if feedback_from_eval else message
        prev_rephrase_text = rephrased_text
        
        logger.warning(
            "Chunk '%s' failed attempt %d. Reason: %s. Feedback for next: %s",
            chunk_header, attempt, message, last_feedback
        )
        if attempt < max_attempts:
            time.sleep(3) # Wait before retrying

    logger.warning(
        "Chunk '%s' failed all %d attempts. Returning best rephrase found.",
        chunk_header, max_attempts
    )
    if best_rephrase_obj:
        best_rephrase_obj['metadata']['status'] = 'best_effort_failed_thresholds'
        return best_rephrase_obj

    logger.error(
        "Chunk '%s' failed all attempts and no rephrase was considered 'best'. "
        "Returning original content.",
        chunk_header
    )
    return {
        'metadata': chunk_data['metadata'],
        'page_content': original_text,
        'status': 'failed_all_attempts_no_best'
    }
