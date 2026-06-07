import json
import logging

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.llm.providers import get_complex_llm
from src.schemas.coverletter_output import CoverLetterOutput
from src.graph.state import JobAssistAgentState

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert career coach who writes compelling, specific cover letters.
Your cover letters are never generic — every sentence is grounded in the candidate's actual experience
and the specific role requirements.
No clichés. No "I am writing to express my interest." No vague claims.

{format_instructions}
"""

USER_PROMPT_TEMPLATE = """Write a cover letter for this candidate applying to this role.

=== Target Role ===
{jd_role} ({jd_seniority} level)

=== JD Analysis (what they value most) ===
{jd_analysis}

=== Execution Plan (candidate's strongest angles) ===
{execution_plan}

=== Candidate's Resume (use specific achievements from here) ===
{resume_text}
"""


def cover_letter_node(state: JobAssistAgentState):
    logger.info("Cover letter generator — starting")

    resume_text = state.get("rewritten_resume", "") or state.get("resume_text", "")
    if not resume_text:
        state["error"] = "Rewritten resume missing. Cannot generate cover letter."
        return state

    try:
        llm = get_complex_llm()

        parser = PydanticOutputParser(pydantic_object=CoverLetterOutput)

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT_TEMPLATE),
        ])

        prompt = prompt_template.format_messages(
            format_instructions=parser.get_format_instructions(),
            jd_role=state.get("jd_role", "the target role"),
            jd_seniority=state.get("jd_seniority", "mid"),
            jd_analysis=state.get("jd_analysis", ""),
            execution_plan=state.get("execution_plan", ""),
            resume_text=resume_text,
        )

        response = llm.invoke(prompt)
        result = parser.parse(response.content)

        state["cover_letter"] = result.cover_letter
        state["cover_letter_subject"] = result.subject_line
        state["status"] = "cover letter generation complete"

        logger.info("cover_letter complete — %d chars", len(result.cover_letter))

        with open("output/cover_letter_result.json", "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, indent=4, ensure_ascii=False)

    except Exception as e:
        logger.exception("cover_letter failed")
        state["error"] = f"Cover letter generation failed: {e}"

    return state