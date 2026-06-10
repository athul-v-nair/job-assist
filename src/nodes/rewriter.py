import json
import logging

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.llm.providers import get_complex_llm
from src.schemas.rewriter_output import RewriterOutput
from src.graph.state import JobAssistAgentState

logger = logging.getLogger(__name__)


# ── Prompts ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an elite resume writer with 15+ years of experience \
helping candidates land roles at top companies.

Your rewrites follow these rules strictly:
1. Choose section headings and order appropriate for the specific role and industry
2. Use strong action verbs (Led, Built, Reduced, Increased, Architected, Delivered, etc.)
3. Add metrics wherever plausible (%, $, time saved, team size, scale)
4. Naturally integrate missing skills only where truthful and relevant — never fabricate
5. Keep every bullet to 1-2 lines maximum
6. Preserve the candidate's original section order and contact information exactly
7. Do not skip/miss any section when rewriting. Include all the sections and important titles from the resume
8. Write the summary to directly mirror the target role's language

{format_instructions}"""

USER_PROMPT_TEMPLATE = """Rewrite the resume below using the execution plan,skill gaps and judge feeback (if available) provided. 

=== Execution Plan (what to emphasise) ===
{execution_plan}

=== Missing Skills (weave in only where truthful) ===
{missing_skills}

=== Original Resume ===
{resume_text}

=== Judge Feedback from previous iteration===
{judge_feedback}
"""


# ── Node ───────────────────────────────────────────────────────────────────────

def resume_rewriter_node(state: JobAssistAgentState):
    logger.info("Resume rewriter — starting")

    resume_text = state.get("rewritten_resume") or state.get("resume_text", "")
    execution_plan = state.get("execution_plan", "")
    missing_skills = state.get("missing_skills", [])
    judge_feedback = state.get("judge_feedback", "")

    if not resume_text:
        state["error"] = "Resume text is missing. Cannot rewrite."
        return state

    if not execution_plan:
        state["error"] = "Execution plan is missing. Run the analyzer node first."
        return state

    try:
        llm = get_complex_llm()

        parser = PydanticOutputParser(pydantic_object=RewriterOutput)

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT_TEMPLATE),
        ])

        prompt = prompt_template.format_messages(
            format_instructions=parser.get_format_instructions(),
            execution_plan=execution_plan,
            missing_skills=", ".join(missing_skills) if missing_skills else "None identified",
            resume_text=resume_text,
            judge_feedback=judge_feedback
        )

        response = llm.invoke(prompt)
        result = parser.parse(response.content)

        state["rewritten_resume"] = result.rewritten_resume
        state["section_order"] = result.section_order
        # state["resume_sections"] = [s.model_dump() for s in result.sections]
        state["status"] = "rewriting complete"

        logger.info("resume_rewriter complete — rewritten resume length: %d chars", len(result.rewritten_resume))

        with open("output/rewriter_result.json", "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, indent=4, ensure_ascii=False)

    except Exception as e:
        logger.exception("resume_rewriter failed")
        state["error"] = f"Resume rewriting failed: {e}"

    return state