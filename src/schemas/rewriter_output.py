from pydantic import BaseModel, Field

class ResumeSection(BaseModel):
    """A single section of the resume."""
    heading: str = Field(
        description="Section heading exactly as it should appear on the resume. "
                    "e.g. 'Work Experience', 'Technical Skills', 'Education', 'Projects', 'Certifications'"
    )
    content: str = Field(
        description="Full content for this section as plain text, preserving bullet points with '•' character. "
                    "Keep original formatting structure within the section."
    )


class RewriterOutput(BaseModel):
    """Structured output from the resume rewriter node."""

    section_order: list[str] = Field(
        description=(
            "Ordered list of section headings appropriate for this specific role and industry. "
            "Example for SWE: ['Contact', 'Summary', 'Technical Skills', 'Work Experience', 'Projects', 'Education']. "
            "Example for hospitality: ['Contact', 'Summary', 'Work Experience', 'Skills', 'Certifications']. "
            "Example for design: ['Contact', 'Summary', 'Portfolio', 'Work Experience', 'Tools', 'Education']. "
            "Always start with Contact and end with Education if present. "
            "Choose headings that make sense for the role — do not force a tech structure onto non-tech roles."
        )
    )
    # sections: list[ResumeSection] = Field(
    #     description="The actual content for each section, in the same order as section_order. "
    #                 "Every heading in section_order must have a corresponding entry here."
    # )

    rewritten_resume: str = Field(
        description=(
            "The fully rewritten resume as a single string. "
            "Must preserve all original sections (contact info, summary, experience, "
            "education, skills) but with improved bullets, stronger action verbs, "
            "quantified results, and missing skills naturally woven in where truthful."
        )
    )