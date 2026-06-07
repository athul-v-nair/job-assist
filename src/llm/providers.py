"""
llm/providers.py — Initialises ChatNVIDIA small and large model instances.

Rule of thumb used across the graph:
  small_llm → structured extraction, scoring, classification  (fast, cheap)
  large_llm → rewriting, coaching, planning                  (powerful, slower)
"""

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from src.config.config import get_settings


def get_simple_llm() -> ChatNVIDIA:
    """
    mistral-7b-instruct — used for:
      - Skill extraction
      - ATS scoring (baseline + re-score)
      - LLM-as-judge quality scoring
    """
    settings = get_settings()
    return ChatNVIDIA(
        model=settings.simple_model,
        api_key=settings.nvidia_api_key,
        temperature=0.1,
    )

def get_complex_llm() -> ChatNVIDIA:
    """
    deepseek-r1-flash — used for:
      - JD analysis + execution planning
      - Resume bullet rewriting
      - Interview question generation
      - Learning plan generation
    """
    settings = get_settings()
    return ChatNVIDIA(
        model=settings.complex_model,
        api_key=settings.nvidia_api_key,
        temperature=0.3,
        max_tokens=2048,
    )