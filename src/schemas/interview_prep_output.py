from pydantic import BaseModel, Field


class InterviewPrepOutput(BaseModel):
    """Structured output from the interview prep node."""

    interview_topics: list[str] = Field(
        description="4-6 high-level topic areas the interviewer will likely cover, "
                    "based on the JD and candidate's profile. "
                    "Examples: 'System Design', 'Python async internals', 'Stakeholder communication'."
    )
    interview_qa: list[dict] = Field(
        description=(
            "8-12 interview questions with short answers, grouped by topic. "
            "Each item must be a dict with exactly these keys: "
            "topic (str — must match one of interview_topics), "
            "question (str — the interview question), "
            "answer (str — concise answer in 2-3 lines, direct and specific)."
        )
    )