from pydantic import BaseModel, Field


class RoadmapOutput(BaseModel):
    """Structured output from the skill gap and roadmap node."""

    skill_gaps: list[str] = Field(
        description="Refined list of skills the candidate is missing for this specific role. "
                    "Be specific — not just 'Python' but 'Python async programming' if that's what's missing."
    )
    skill_roadmap: list[dict] = Field(
        description=(
            "Ordered learning roadmap for each skill gap. "
            "Each item must be a dict with exactly these keys: "
            "skill (str), why (str — one sentence on why it matters for this role), "
            "resource (str — specific resource: course name, book, or practice site), "
            "duration (str — realistic estimate e.g. '3 days', '1 week')."
        )
    )