# JobAssist — AI Resume & Career Agent

An end-to-end AI agent that takes your resume and a job description, then produces a fully rewritten resume, cover letter, skill gap roadmap, and interview preparation kit — powered by LangGraph, NVIDIA NIM, and Streamlit.

---

## What it does

| Output | Description |
|--------|-------------|
| **Resume Rewrite** | ATS-optimised rewrite with role-aware section structure |
| **Cover Letter** | Tailored, specific cover letter — no generic openers |
| **Skill Gap Analysis** | Matched vs missing skills with ATS and match % scores |
| **Learning Roadmap** | Ordered upskilling plan with real resources and durations |
| **Interview Prep** | Key topics + Q&A grouped by topic with concise answers |

---

## Architecture

```
Resume PDF + Job Description
        ↓
resume_jd_analyzer       LLM — extract role, skills, execution plan, ATS baseline
        ↓ [route_after_score]
        ├── baseline good ──────────────────────────────┐
        └── needs improvement → resume_rewriter          │
                ↓                                        │
            rescorer         LLM — re-score + judge     │
                ↓ [route_after_score]                   │
                ├── threshold met ──────────────────────┤
                └── loop back to rewriter (max 3x)      │
                                                        ↓
                                              cover_letter      LLM
                                                        ↓
                                              skill_gap_roadmap LLM
                                                        ↓
                                              interview_prep    LLM
                                                        ↓
                                                       END
```

**Thresholds** (configurable):
- ATS Score ≥ 80
- Match Percentage ≥ 75
- Max rewrite iterations: 3

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent framework | LangGraph |
| LLM provider | NVIDIA NIM (ChatNVIDIA) |
| LLM model | `meta/llama-3.1-70b-instruct` |
| Output parsing | LangChain `PydanticOutputParser` |
| Observability | LangSmith |
| PDF parsing | PyMuPDF (fitz) |
| Frontend | Streamlit |

---

## Project Structure

```
job-assist/
├── src/
│   ├── nodes/
│   │   ├── analyzer.py          # Node 1 — JD analysis + ATS baseline
│   │   ├── rewriter.py          # Node 2 — Resume rewriting
│   │   ├── rescorer.py          # Node 3 — Re-score + LLM judge
│   │   ├── cover_letter.py      # Node 4 — Cover letter generation
│   │   ├── skill_gap_roadmap.py # Node 5 — Skill gap + learning roadmap
│   │   └── interview_prep.py    # Node 6 — Interview topics + Q&A
│   ├── graph/
│   │   ├── state.py             # JobAssistAgentState TypedDict
│   │   └── graph.py             # LangGraph builder + conditional routing
│   ├── schemas/                 # Pydantic output models per node
│   ├── llm/
│   │   └── providers.py         # ChatNVIDIA model instances
│   ├── tools/
│   │   └── pdf_parser.py        # PyMuPDF resume extraction
│   └── config.py                # Settings (thresholds, model names, keys)
├── ui/
│   ├── app.py                   # Streamlit entrypoint
│   ├── components.py            # Reusable render functions
│   └── styles.css               # Custom CSS — editorial dark theme
├── output/                      # Generated JSON outputs (gitignored)
├── .env                         # API keys (never commit)
├── pyproject.toml
└── README.md
```

---

## Setup

### 1. Clone and create virtual environment

```bash
git clone <repo>
cd job-assist
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -e .
```

### 3. Configure environment

Create a `.env` file in the project root:

```env
# NVIDIA NIM
NVIDIA_API_KEY=your_nvidia_api_key_here

# LangSmith (optional but recommended)
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT=job-assist
LANGCHAIN_TRACING_V2=true

# Agent thresholds
ATS_THRESHOLD=80
MATCH_THRESHOLD=75
MAX_ITERATIONS=3
```

Get your NVIDIA API key: https://build.nvidia.com

### 4. Run the UI

```bash
streamlit run ui/app.py
```

Open http://localhost:8501

---

## Running the agent directly (no UI)

```python
from src.graph.graph import build_graph
from src.tools.pdf_parser import parse_resume_pdf

with open("resume.pdf", "rb") as f:
    parsed = parse_resume_pdf(f.read())

graph = build_graph()
result = graph.invoke({
    "resume_text":     parsed.raw_text,
    "job_description": "paste JD here",
    "iteration":       0,
})

print(result["rewritten_resume"])
print(result["cover_letter"])
```

---

## LangSmith Observability

Every graph run is traced automatically when `LANGSMITH_API_KEY` is set. Each LLM call shows latency, token count, prompt, and response.

Dashboard: https://smith.langchain.com

---

## Notes

- Upload text-based PDFs only — scanned PDFs will produce poor results
- The rewrite loop runs up to `MAX_ITERATIONS` times automatically; no manual intervention needed
- All intermediate outputs are saved to `output/*.json` for inspection