import json
import logging

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.llm.providers import get_complex_llm
from src.schemas.roadmap_output import RoadmapOutput
from src.graph.state import JobAssistAgentState

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a senior technical career coach specialising in upskilling plans.
You identify precise skill gaps and create realistic, actionable learning roadmaps.
Resources must be real and specific — no generic advice.

{format_instructions}"""

USER_PROMPT_TEMPLATE = """Build a skill gap analysis and learning roadmap for this candidate.

=== Target Role ===
{jd_role} ({jd_seniority} level)

=== Skills Required by JD ===
{jd_skills}

=== Skills Missing from Candidate's Resume ===
{missing_skills}

=== JD Analysis (for context on what matters most) ===
{jd_analysis}

Rules:
- skill_gaps: be surgical — only include gaps that actually matter for this role
- skill_roadmap: order by priority (most critical for the role first)
- resource: be specific e.g. "FastAPI official docs + Build a REST API tutorial", 
  "Designing Data-Intensive Applications — chapters 1-3", "LeetCode Blind 75"
- duration: be honest and realistic"""


def roadmap_node(state: JobAssistAgentState):
    logger.info("Skill gap roadmap — starting")

    missing_skills = state.get("missing_skills", [])
    if not missing_skills:
        logger.info("skill_gap_roadmap: no missing skills — skipping node")
        state["skill_gaps"] = []
        state["skill_roadmap"] = []
        return state

    try:
        llm = get_complex_llm()

        parser = PydanticOutputParser(pydantic_object=RoadmapOutput)

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT_TEMPLATE),
        ])

        prompt = prompt_template.format_messages(
            format_instructions=parser.get_format_instructions(),
            jd_role=state.get("jd_role", "the target role"),
            jd_seniority=state.get("jd_seniority", "mid"),
            jd_skills=", ".join(state.get("jd_skills", [])) or "See JD",
            missing_skills=", ".join(missing_skills),
            jd_analysis=state.get("jd_analysis", ""),
        )

        response = llm.invoke(prompt)
        result = parser.parse(response.content)

        state["skill_gaps"] = result.skill_gaps
        state["skill_roadmap"] = result.skill_roadmap
        state["status"] = "roadmap creation complete"

        logger.info(
            "skill_gap_roadmap complete — %d gaps, %d roadmap items",
            len(result.skill_gaps),
            len(result.skill_roadmap),
        )

        with open("output/skill_gap_roadmap_result.json", "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, indent=4, ensure_ascii=False)

    except Exception as e:
        logger.exception("skill_gap_roadmap failed")
        state["error"] = f"Skill gap roadmap failed: {e}"

    return state