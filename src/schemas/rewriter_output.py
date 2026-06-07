from pydantic import BaseModel, Field


class RewriterOutput(BaseModel):
    """Structured output from the resume rewriter node."""

    rewritten_resume: str = Field(
        description=(
            "The fully rewritten resume as a single string. "
            "Must preserve all original sections (contact info, summary, experience, "
            "education, skills) but with improved bullets, stronger action verbs, "
            "quantified results, and missing skills naturally woven in where truthful."
        )
    )