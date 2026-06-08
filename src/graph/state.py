from typing import TypedDict, Optional

class JobAssistAgentState(TypedDict):
    # ── Raw Inputs ──────────────────────────────────────
    resume_text: str
    job_description: str

    # ── JD Analyzer ──────────────────────────────────────
    jd_skills: list[str]           # Skills required by the JD
    jd_role: str                   # Inferred job title/role
    jd_seniority: str              # junior / mid / senior / lead
    jd_analysis: str               # Full structured analysis text
    execution_plan: str            # Planner output (what to focus on)

    # ── ATS Scorer (baseline) ────────────────────────────
    matched_skills: list[str]      # Skills that match with Job description
    missing_skills: list[str]      # In JD but not in resume
    strengths: list[str]    
    weakness: list[str]      
    baseline_ats_score: int        # 0-100, before rewriting
    baseline_match_percentage: int # 0-100, resume vs JD overlap

    # ── Resume Rewriter ───────────────────────────────────
    rewritten_resume: str          # Full rewritten resume text
    section_order: list[str]       # LLM-decided section order for this role
    resume_sections: list[dict]    # [{heading, content}] — used by resume PDF node

    # ── Re-scorer ─────────────────────────────────────────
    improved_ats_score: int        # 0-100, after rewriting
    improved_match_percentage: int # 0-100, after rewriting
    judge_score: int               # LLM-as-judge quality score (0-10)
    judge_feedback: str            # Judge's reasoning / suggestions

    # ── Cover Letter ─────────────────────────────────────────────────
    cover_letter: str
    cover_letter_subject: str

    # ── Roadmap and Resources ─────────────────────
    skill_gaps: list[str]          # refined missing skills specific to this role
    skill_roadmap: list[dict]      # [{skill, why, resource, duration}]

    # ── Preparation Helper ───────────────────────────────────
    interview_topics: list[str]    # High-level topic areas
    interview_questions: list[str] # Specific practice questions

    # ── Control flow ──────────────────────────────────────────────
    iteration: int                 # How many "Improve Again" cycles run
    error: Optional[str]           # Set if any node fails; graph stops early
    status: str                    # current node name for UI progress