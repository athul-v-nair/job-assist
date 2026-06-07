"""
config.py — Single source of truth for all settings.
Loaded once at startup; everything else imports from here.
"""
 
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
 
    # ── NVIDIA ────────────────────────────────────────────────────
    nvidia_api_key: str = os.getenv('NVIDIA_API_KEY')
    simple_model: str = os.getenv('SIMPLE_MODEL')
    complex_model: str = os.getenv('COMPLEX_MODEL')
 
    # ── LangSmith ─────────────────────────────────────────────────
    langsmith_api_key: str = os.getenv('LANGSMITH_API_KEY')
    langsmith_project: str = os.getenv('LANGSMITH_PROJECT')
    langchain_tracing_v2: str = os.getenv('LANGSMITH_TRACING')
    langchain_endpoint: str = os.getenv('LANGSMITH_ENDPOINT')
 
    # ── FastAPI ───────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    allowed_origins: str = "http://localhost:8501"
 
    # ── Agent ─────────────────────────────────────────────────────
    ATS_THRESHOLD = 80    # minimum improved_ats_score to pass
    MATCH_THRESHOLD = 75  # minimum improved_match_percentage to pass
    MAX_ITERATIONS = 3    # max rewrite loops before forcing END

def get_settings():
    return Settings