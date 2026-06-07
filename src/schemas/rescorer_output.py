from pydantic import BaseModel, Field


class RescorerOutput(BaseModel):
    """Structured output from the rescorer / LLM-as-judge node."""

    improved_ats_score: int = Field(
        description="ATS compatibility score 0-100 for the rewritten resume. "
                    "Criteria: keyword match with JD (40%), structure and formatting (30%), "
                    "role relevance (30%)."
    )
    improved_match_percentage: int = Field(
        description="Percentage of JD-required skills present in the rewritten resume. 0-100."
    )
    judge_score: int = Field(
        description="Overall resume quality score 0-10. "
                    "0-3: poor, 4-6: acceptable, 7-8: good, 9-10: excellent."
    )
    judge_feedback: str = Field(
        description="Specific, surgical feedback for the next rewrite iteration. "
                    "Name exact bullets to fix, exact skills still missing, exact weak phrases. "
                    "If thresholds are met write: 'Resume meets quality threshold. Ready to proceed.'"
    )
    iteration: int = Field(
        description="Keeping count of the iterations performed."
    )