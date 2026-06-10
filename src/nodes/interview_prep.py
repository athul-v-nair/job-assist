import json
import logging

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.llm.providers import get_complex_llm
from src.schemas.interview_prep_output import InterviewPrepOutput
from src.graph.state import JobAssistAgentState

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a senior technical interview coach.
You generate highly targeted interview questions and concise answers based on 
a specific role and candidate profile.
Every question must be something a real interviewer would actually ask.

{format_instructions}"""

USER_PROMPT_TEMPLATE = """Generate interview preparation material for this candidate.

=== Target Role ===
{jd_role} ({jd_seniority} level)

=== JD Analysis ===
{jd_analysis}

=== Skills Required ===
{jd_skills}

=== Candidate's Skill Gaps ===
{skill_gaps}

Rules:
- interview_topics: 4-6 areas, cover both technical and behavioral
- interview_qa: 8-12 questions total, spread across all topics (2-3 per topic)
- Mix question types: behavioral (STAR expected), technical concept, practical/scenario
- answer: 2-3 lines max — direct, specific, no fluff
- For behavioral questions the answer should outline the ideal STAR structure, not a generic answer"""


def interview_prep_node(state: JobAssistAgentState):
    logger.info("Interview prep — starting")

    try:
        llm = get_complex_llm()

        parser = PydanticOutputParser(pydantic_object=InterviewPrepOutput)

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT_TEMPLATE),
        ])

        prompt = prompt_template.format_messages(
            format_instructions=parser.get_format_instructions(),
            jd_role=state.get("jd_role", "the target role"),
            jd_seniority=state.get("jd_seniority", "mid"),
            jd_analysis=state.get("jd_analysis", ""),
            jd_skills=", ".join(state.get("jd_skills", [])) or "See JD",
            skill_gaps=", ".join(state.get("skill_gaps", [])) or "None identified",
        )

        response = llm.invoke(prompt)
        result = parser.parse(response.content)

        state["interview_topics"] = result.interview_topics
        state["interview_questions"] = result.interview_qa

        logger.info(
            "interview_prep complete — %d topics, %d questions",
            len(result.interview_topics),
            len(result.interview_qa),
        )

        with open("output/interview_prep_result.json", "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, indent=4, ensure_ascii=False)

    except Exception as e:
        logger.exception("interview_prep failed")
        state["error"] = f"Interview prep failed: {e}"

    return state