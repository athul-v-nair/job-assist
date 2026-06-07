from pydantic import BaseModel, Field
from typing import List, Literal

class AnalysisOutput(BaseModel):
    jd_role: str = Field(
        description="Exact job title from the posting"
    )

    jd_seniority: Literal[
        "junior",
        "mid",
        "senior",
        "lead",
        "principal",
        "staff",
    ] = Field(
        description="Seniority level inferred from the JD"
    )

    jd_skills: List[str] = Field(
        description="List of technical and soft skills required"
    )

    jd_analysis: str = Field(
        description=(
            "2-3 sentence summary of what this role is really about and what the company values most"
        )
    )

    execution_plan: str = Field(
        description=(
            "Maximum 5 sentences actionable strategy for tailoring a resume to this role"
        )
    )

    ats_score: int = Field(
        ge=0,
        le=100,
        description="ATS compatibility score from 0-100"
    )

    match_percentage: int = Field(
        ge=0,
        le=100,
        description="Overall resume match percentage for this job from 0-100"
    )

    matched_skills: List[str] = Field(
        description="Skills found in both resume and job description"
    )

    missing_skills: List[str] = Field(
        description="Important JD skills missing from the resume"
    )

    strengths: List[str] = Field(
        description="Points that add strength to the resume with respect to job description"
    )

    gaps: List[str] = Field(
        description="Gaps that are found in resume with respect to job description"
    )