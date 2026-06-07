import json
import logging

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.llm.providers import get_complex_llm
from src.schemas.rescorer_output import RescorerOutput
from src.graph.state import JobAssistAgentState

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a strict ATS evaluator and resume quality judge.
Your role is to score a rewritten resume and provide precise, actionable feedback \
so the rewriter can improve it further if needed.

Be ruthlessly honest — vague feedback wastes an iteration.

{format_instructions}"""

USER_PROMPT_TEMPLATE = """Evaluate this rewritten resume against the job requirements.

=== Target Role ===
{jd_role} ({jd_seniority} level)

=== JD Skills Required ===
{jd_skills}

=== Missing Skills from Original Resume ===
{missing_skills}

=== Rewritten Resume ===
{rewritten_resume}

=== Previous Judge Feedback (iteration {iteration}) ===
{previous_feedback}"""


def rescorer_node(state: JobAssistAgentState):
    logger.info("Rescorer — starting (iteration %d)", state.get("iteration", 0))

    rewritten_resume = state.get("rewritten_resume", "")
    if not rewritten_resume:
        state["error"] = "Rewritten resume is missing. Run the rewriter node first."
        return state

    try:
        llm = get_complex_llm()

        parser = PydanticOutputParser(pydantic_object=RescorerOutput)

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT_TEMPLATE),
        ])

        prompt = prompt_template.format_messages(
            format_instructions=parser.get_format_instructions(),
            jd_role=state.get("jd_role", "the target role"),
            jd_seniority=state.get("jd_seniority", "mid"),
            jd_skills=", ".join(state.get("jd_skills", [])) or "See JD",
            missing_skills=", ".join(state.get("missing_skills", [])) or "None",
            rewritten_resume=rewritten_resume,
            iteration=state.get("iteration", 0),
            previous_feedback=state.get("judge_feedback", "First evaluation — no previous feedback."),
        )

        response = llm.invoke(prompt)
        result = parser.parse(response.content)

        state["improved_ats_score"] = result.improved_ats_score
        state["improved_match_percentage"] = result.improved_match_percentage
        state["judge_score"] = result.judge_score
        state["judge_feedback"] = result.judge_feedback
        state["iteration"] = result.iteration + 1
        state["status"] = "rescoring complete"

        logger.info(
            "rescorer complete — ATS: %d | match: %d%% | judge: %d/10",
            result.improved_ats_score,
            result.improved_match_percentage,
            result.judge_score,
        )

        with open("output/rescorer_result.json", "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, indent=4, ensure_ascii=False)

    except Exception as e:
        logger.exception("rescorer failed")
        state["error"] = f"Rescoring failed: {e}"

    return state