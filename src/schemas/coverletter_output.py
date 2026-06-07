from pydantic import BaseModel, Field


class CoverLetterOutput(BaseModel):
    """Structured output from the cover letter generator node."""

    subject_line: str = Field(
        description="Email subject line for sending the application. "
                    "e.g. 'Application for Senior Backend Engineer — John Smith'"
    )
    cover_letter: str = Field(
        description=(
            "Full cover letter as plain text, 3-4 paragraphs. "
            "Para 1: Opening — role applied for + one strong hook about the candidate. "
            "Para 2: Why this candidate fits — 2-3 specific achievements mapped to JD requirements. "
            "Para 3: Why this company/role specifically — shows genuine interest. "
            "Para 4: Call to action — professional close. "
            "Tone: confident, specific, not generic. No 'I am writing to apply' openers."
        )
    )