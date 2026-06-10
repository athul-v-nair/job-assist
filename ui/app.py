"""
ui/app.py — Streamlit entrypoint.

Run from project root:
    streamlit run ui/app.py

The graph lives in src/ — we add the project root to sys.path so imports work.
"""

import sys
import json
import logging
from pathlib import Path

# ── Make src/ importable when running from project root ──────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st

from src.graph.graph import build_graph
from src.tools.pdf_parser import parse_pdf          # your existing parser

from ui.components import (
    render_masthead,
    render_pipeline,
    render_resume_tab,
    render_cover_letter_tab,
    render_skills_tab,
    render_roadmap_tab,
    render_interview_tab,
    render_empty_state,
    PIPELINE_STEPS,
)

logging.basicConfig(level=logging.INFO)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JobAssist — AI Career Agent",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load CSS ──────────────────────────────────────────────────────────────────
css_path = Path(__file__).parent / "styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "result"     not in st.session_state: st.session_state.result     = None
if "completed"  not in st.session_state: st.session_state.completed  = []
if "active"     not in st.session_state: st.session_state.active     = ""
if "run_error"  not in st.session_state: st.session_state.run_error  = ""


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">Job<em>Assist</em></div>
    <div class="sidebar-tagline">AI-powered career preparation</div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)
    resume_file = st.file_uploader(
        "Upload Resume",
        type=["pdf"],
        help="Text-based PDF only (not scanned)",
    )

    st.markdown("<span class='sidebar-section-label' style='margin-top:1rem;display:block'>Job Description</span>",
                unsafe_allow_html=True)
    jd_text = st.text_area(
        "Job Description", height=240,
        placeholder="Paste the full job posting here…",
        label_visibility="collapsed",
    )

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)
    run_btn = st.button(
        "⚡  Run Analysis",
        disabled=not (resume_file and jd_text.strip()),
    )

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)
    render_pipeline(
        completed=st.session_state.completed,
        active=st.session_state.active,
        error=st.session_state.run_error,
    )


# ── Graph runner ──────────────────────────────────────────────────────────────
def run_graph(pdf_bytes: bytes, job_description: str) -> dict:
    """
    Run the full LangGraph pipeline with live pipeline step updates.
    Uses st.status for a progress block, updates sidebar pipeline steps.
    """
    # Parse PDF
    parsed = parse_pdf(pdf_bytes)

    initial_state = {
        "resume_text":     parsed.raw_text,
        "job_description": job_description,
        "iteration":       0,
        "status":          "starting",
    }

    completed = []
    step_keys = [k for k, _ in PIPELINE_STEPS]

    graph = build_graph()

    with st.status("Running analysis pipeline…", expanded=True) as status_block:
        for step_key, step_label in PIPELINE_STEPS:
            st.write(f"▸ {step_label}…")
            st.session_state.active = step_key
            st.session_state.completed = completed.copy()

        # Run the full graph — LangGraph handles the loop internally
        final_state = graph.invoke(initial_state)

        # Mark all nodes that produced output as completed
        for step_key, _ in PIPELINE_STEPS:
            completed.append(step_key)

        status_block.update(label="Analysis complete ✓", state="complete", expanded=False)

    st.session_state.completed = completed
    st.session_state.active    = ""
    return final_state


# ── Main area ─────────────────────────────────────────────────────────────────
if run_btn and resume_file and jd_text.strip():
    st.session_state.result    = None
    st.session_state.completed = []
    st.session_state.run_error = ""

    try:
        result = run_graph(resume_file.getvalue(), jd_text.strip())
        if result.get("error"):
            st.session_state.run_error = result["error"]
            st.error(f"Pipeline error: {result['error']}")
        else:
            st.session_state.result = result
            st.rerun()
    except Exception as e:
        st.session_state.run_error = str(e)
        st.error(f"Unexpected error: {e}")


# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result
    
    render_masthead(
        jd_role=r.get("jd_role", ""),
        jd_seniority=r.get("jd_seniority", ""),
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "✍  Resume",
        "✉  Cover Letter",
        "◎  Skills",
        "↑  Roadmap",
        "?  Interview Prep",
    ])

    with tab1: render_resume_tab(r)
    with tab2: render_cover_letter_tab(r)
    with tab3: render_skills_tab(r)
    with tab4: render_roadmap_tab(r)
    with tab5: render_interview_tab(r)

    # Debug expander — useful during demo
    with st.expander("Raw state (debug)", expanded=False):
        st.json({k: v for k, v in r.items() if k not in ("resume_text", "job_description")})

else:
    render_masthead()
    render_empty_state()