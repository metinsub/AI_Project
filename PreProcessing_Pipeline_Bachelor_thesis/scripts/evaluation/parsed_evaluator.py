"""
Defines the Pydantic models for parsing and validating the LLM evaluator's output.

This module contains the data structures for:
- Individual metric scores.
- The overall result of an evaluation, including scores, identified issues,
  and textual feedback.
"""

from typing import List
from pydantic import BaseModel, Field


class Scores(BaseModel):
    correctness: float = Field(..., ge=0.0, le=1.0)
    completeness: float = Field(..., ge=0.0, le=1.0)
    consistency: float = Field(..., ge=0.0, le=1.0)
    relevance: float = Field(..., ge=0.0, le=1.0)
    interpretability: float = Field(..., ge=0.0, le=1.0)

class EvaluatorResult(BaseModel):
    scores: Scores
    missing_items: List[str]
    hallucinated_items: List[str]
    feedback: str

    class Config:
        extra = "forbid"  # disallow extra fields
