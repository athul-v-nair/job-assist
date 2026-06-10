"""
ui/components.py — Reusable render functions.
Each function takes data and calls st.markdown with unsafe_allow_html=True.
No graph logic here — pure presentation.
"""
import streamlit as st


# ── Helpers ───────────────────────────────────────────────────────────────────

def _score_class(score: int) -> str:
    if score >= 80: return "num-green"
    if score >= 65: return "num-yellow"
    if score >= 50: return "num-orange"
    return "num-red"


def _esc(text: str) -> str:
    """Minimal HTML escape for user content injected into HTML blocks."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ── Masthead ──────────────────────────────────────────────────────────────────

def render_masthead(jd_role: str = "", jd_seniority: str = "") -> None:
    role_line = f"<span class='masthead-sub'>{_esc(jd_role)} · {_esc(jd_seniority.capitalize())}</span>" if jd_role else ""
    st.markdown(f"""
    <div class="masthead">
        <div>
            <div class="masthead-title">Job<em>Assist</em></div>
            <div>{role_line}</div>
        </div>
        <div class="masthead-sub">
            AI · Resume · Career
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Pipeline sidebar ──────────────────────────────────────────────────────────

PIPELINE_STEPS = [
    ("resume_jd_analyzer", "Analyze Resume & JD"),
    ("resume_rewriter",    "Rewrite Resume"),
    ("rescorer",           "Rescore & Judge"),
    ("cover_letter",       "Cover Letter"),
    ("skill_gap_roadmap",  "Skill Gap Roadmap"),
    ("interview_prep",     "Interview Prep"),
]

def render_pipeline(completed: list[str], active: str = "", error: str = "") -> None:
    st.markdown("<div class='pipeline-label'>Pipeline</div>", unsafe_allow_html=True)
    for key, label in PIPELINE_STEPS:
        if key == active:
            cls, dot = "step-running", "dot-running"
        elif key in completed:
            cls, dot = "step-done", "dot-done"
        elif error and key not in completed:
            cls, dot = "step-idle", "dot-idle"
        else:
            cls, dot = "step-idle", "dot-idle"

        icon = "✓ " if key in completed else ""
        st.markdown(f"""
        <div class="pipeline-step {cls}">
            <div class="step-dot {dot}"></div>
            {icon}{label}
        </div>
        """, unsafe_allow_html=True)


# ── Score cards ───────────────────────────────────────────────────────────────

def render_scores(state: dict) -> None:
    baseline  = state.get("baseline_ats_score", 0)
    improved  = state.get("improved_ats_score", 0)
    match_b   = state.get("baseline_match_percentage", 0)
    match_i   = state.get("improved_match_percentage", 0)
    judge     = state.get("judge_score", 0)
    iteration = state.get("iteration", 0)
            
    def card(label, value, suffix, cls):
        return f"""
        <div class="score-card">
            <div class="score-num {cls}">
                {value}{suffix}
            </div>
            <div class="score-lbl">
                {label}
            </div>
        </div>"""

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(card("Baseline ATS", baseline, "%", _score_class(baseline)), unsafe_allow_html=True)
    with c2:
        st.markdown(card("Improved ATS", improved, "%", _score_class(improved)), unsafe_allow_html=True)
    with c3:
        match = match_i or match_b
        st.markdown(card("Match Score", match, "%", _score_class(match)), unsafe_allow_html=True)
    with c4:
        st.markdown(card("Judge Score", judge, "/10", _score_class(judge * 10)), unsafe_allow_html=True)

# ── Skill tags ────────────────────────────────────────────────────────────────

def render_skill_section(matched: list[str], missing: list[str]) -> None:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-eyebrow'>✓ Matched Skills</div>", unsafe_allow_html=True)
        tags = "".join(f"<span class='tag tag-match'>{_esc(s)}</span>" for s in matched)
        st.markdown(f"<div class='tag-wrap'>{tags or '<span style=\"color:var(--text-3)\">None found</span>'}</div>",
                    unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='section-eyebrow'>✗ Missing Skills</div>", unsafe_allow_html=True)
        tags = "".join(f"<span class='tag tag-missing'>{_esc(s)}</span>" for s in missing)
        st.markdown(f"<div class='tag-wrap'>{tags or '<span style=\"color:var(--text-3)\">None — great match!</span>'}</div>",
                    unsafe_allow_html=True)


# ── Section box ───────────────────────────────────────────────────────────────

def render_section_box(eyebrow: str, content: str) -> None:
    st.markdown(f"""
    <div class="section-box">
        <div class="section-eyebrow">{eyebrow}</div>
        <div class="section-body">{_esc(content)}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Rewritten resume tab ──────────────────────────────────────────────────────

def render_resume_tab(state: dict) -> None:
    rewritten = state.get("rewritten_resume", "")
    if not rewritten:
        st.info("Resume not yet rewritten.")
        return

    col1, col2 = st.columns([2, 1], gap="large")
    with col1:
        st.markdown("<div class='section-eyebrow'>Rewritten Resume</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='resume-block'>{_esc(rewritten)}</div>", unsafe_allow_html=True)

    with col2:
        render_section_box("JD Analysis", state.get("jd_analysis", ""))
        render_section_box("Execution Plan", state.get("execution_plan", ""))

        st.markdown("<div class='section-eyebrow' style='margin-top:1rem'>Judge Feedback</div>",
                    unsafe_allow_html=True)
        feedback = state.get("judge_feedback", "")
        if feedback:
            render_section_box("", feedback)


# ── Cover letter tab ──────────────────────────────────────────────────────────

def render_cover_letter_tab(state: dict) -> None:
    subject = state.get("cover_letter_subject", "")
    letter  = state.get("cover_letter", "")

    if not letter:
        st.info("Cover letter not yet generated.")
        return

    if subject:
        st.markdown(f"<div class='cover-subject'>Subject: {_esc(subject)}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='resume-block'>{_esc(letter)}</div>", unsafe_allow_html=True)
    st.download_button("⬇ Download Cover Letter", data=letter,
                       file_name="cover_letter.txt", mime="text/plain")


# ── Skills tab ────────────────────────────────────────────────────────────────

def render_skills_tab(state: dict) -> None:
    render_scores(state)
    render_skill_section(
        state.get("matched_skills", []),
        state.get("missing_skills", []),
    )

    col1, col2 = st.columns(2, gap="large")
    with col1:
        strengths = state.get("strengths", [])
        if strengths:
            # st.markdown("<div class='section-eyebrow' style='margin-top:1rem'>Strengths</div>",
            st.markdown("<div class='section-eyebrow' style='margin-top:1rem'>Strengths",
                        unsafe_allow_html=True)
            for s in strengths:
                st.markdown(f"<div class='roadmap-card'><div class='roadmap-skill'>↑ {_esc(s)}</div></div>",
                            unsafe_allow_html=True)
    with col2:
        weaknesses = state.get("weakness", [])
        if weaknesses:
            # st.markdown("<div class='section-eyebrow' style='margin-top:1rem'>Weaknesses</div>",
            st.markdown("<div class='section-eyebrow' style='margin-top:1rem'>Weaknesses",
                        unsafe_allow_html=True)
            for w in weaknesses:
                st.markdown(f"<div class='roadmap-card' style='border-left-color:var(--accent-red)'>"
                            f"<div class='roadmap-skill' style='color:var(--accent-red)'>↓ {_esc(w)}</div></div>",
                            unsafe_allow_html=True)


# ── Roadmap tab ───────────────────────────────────────────────────────────────

def render_roadmap_tab(state: dict) -> None:
    skill_gaps    = state.get("skill_gaps", [])
    skill_roadmap = state.get("skill_roadmap", [])

    if not skill_gaps and not skill_roadmap:
        st.info("Roadmap not yet generated.")
        return

    if skill_gaps:
        st.markdown("<div class='section-eyebrow'>Skill Gaps to Close</div>", unsafe_allow_html=True)
        tags = "".join(f"<span class='tag tag-missing'>{_esc(g)}</span>" for g in skill_gaps)
        st.markdown(f"<div class='tag-wrap' style='margin-bottom:1.5rem'>{tags}</div>",
                    unsafe_allow_html=True)

    if skill_roadmap:
        st.markdown("<div class='section-eyebrow'>Learning Roadmap</div>", unsafe_allow_html=True)
        for item in skill_roadmap:
            skill    = _esc(item.get("skill", ""))
            why      = _esc(item.get("why", ""))
            resource = _esc(item.get("resource", ""))
            duration = _esc(item.get("duration", ""))
            st.markdown(f"""
            <div class="roadmap-card">
                <div class="roadmap-skill">{skill}</div>
                <div class="roadmap-why">{why}</div>
                <div class="roadmap-meta">
                    <span><strong>Resource</strong> {resource}</span>
                    <span><strong>Time</strong> {duration}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ── Interview prep tab ────────────────────────────────────────────────────────

def render_interview_tab(state: dict) -> None:
    topics = state.get("interview_topics", [])
    # qa     = state.get("interview_qa", [])
    qa     = state.get("interview_questions", [])

    if not topics and not qa:
        st.info("Interview prep not yet generated.")
        return

    if topics:
        st.markdown("<div class='section-eyebrow'>Key Topics</div>", unsafe_allow_html=True)
        tags = "".join(f"<span class='tag tag-neutral'>{_esc(t)}</span>" for t in topics)
        st.markdown(f"<div class='tag-wrap' style='margin-bottom:1.5rem'>{tags}</div>",
                    unsafe_allow_html=True)

    if qa:
        st.markdown("<div class='section-eyebrow'>Questions & Answers</div>", unsafe_allow_html=True)
        # Group by topic
        topic_order = topics if topics else list({item.get("topic", "") for item in qa})
        grouped: dict[str, list] = {}
        for item in qa:
            t = item.get("topic", "General")
            grouped.setdefault(t, []).append(item)

        for topic in topic_order:
            items = grouped.get(topic, [])
            if not items:
                continue
            st.markdown(f"<div class='qa-topic-label'>{_esc(topic)}</div>", unsafe_allow_html=True)
            for item in items:
                q = _esc(item.get("question", ""))
                a = _esc(item.get("answer", ""))
                st.markdown(f"""
                <div class="qa-card">
                    <div class="qa-q">Q: {q}</div>
                    <div class="qa-a">{a}</div>
                </div>
                """, unsafe_allow_html=True)


# ── Empty state ───────────────────────────────────────────────────────────────

def render_empty_state() -> None:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">◈</div>
        <div class="empty-title">Ready when you are</div>
        <div class="empty-sub">
            Upload your resume PDF and paste a job description.<br>
            The agent will analyze, rewrite, score, and generate<br>
            your full interview preparation kit.
        </div>
    </div>
    """, unsafe_allow_html=True)