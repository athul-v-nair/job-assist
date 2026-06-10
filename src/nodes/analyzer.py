from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.graph.state import JobAssistAgentState
from src.schemas.analyzer_output import AnalysisOutput
from src.llm.providers import get_complex_llm
import json

import logging
logger = logging.getLogger(__name__)

# ----------------------------------
# Creating the required prompts
# ----------------------------------
SYSTEM_PROMPT = """
You are an expert technical recruiter and career coach with 15+ years of experience.
Your job is to deeply analyze job descriptions and extract actionable intelligence.
Always respond in valid JSON only. No markdown, no explanation outside the JSON.
"""

USER_PROMPT_TEMPLATE = """Analyze the following resume against the job description.

Return a JSON object only.

{format_instructions}

Scoring Rules:
- ats_score = estimate ATS optimization quality (keywords, formatting relevance, alignment)
- match_percentage = estimate overall candidate-job fit
- Be realistic and strict
- missing_skills should include important technologies or business skills absent from the resume
- matched_skills should only include skills clearly present in BOTH documents

Resume:
---
{resume_text}
---

Job Description:
---
{job_description}
---
"""


def resume_jd_analyzer_node(state: JobAssistAgentState):
    logger.info("Resume - JD analysis Starting")
    
    resume_text = state.get("resume_text", "")
    job_description = state.get("job_description", "")
    if not job_description or not resume_text:
        state["error"] = "Input is missing. Provide valid input"
        return state
    
    try:
        llm = get_complex_llm()

        # Creating an output parser
        parser = PydanticOutputParser(pydantic_object=AnalysisOutput)

        # Build prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ('system', SYSTEM_PROMPT),
            ('human', USER_PROMPT_TEMPLATE)
        ])

        prompt = prompt_template.format_messages(
            format_instructions=parser.get_format_instructions(),
            resume_text=resume_text,
            job_description=job_description,
        )

        # Invoke model
        response = llm.invoke(prompt)

        result = parser.parse(response.content)

        # Persist into graph state
        state["jd_role"] = result.jd_role
        state["jd_seniority"] = result.jd_seniority
        state["jd_skills"] = result.jd_skills
        state["jd_analysis"] = result.jd_analysis
        state["execution_plan"] = result.execution_plan
        
        state["baseline_ats_score"] = result.ats_score
        state["baseline_match_percentage"] = result.match_percentage
        state["matched_skills"] = result.matched_skills
        state["missing_skills"] = result.missing_skills
        state["strengths"] = result.strengths
        state["gaps"] = result.gaps
        
        state["status"] = "analysis complete"

        logger.info(
            "jd_analyzer complete — role: %s, skills found: %d",
            result.jd_role,
            len(result.jd_skills),
        )

        # pretty printing into a file -> remove when deploying
        with open("output/analyzer_result.json", "w", encoding="utf-8") as f:
            json.dump(
                result.model_dump(),
                f,
                indent=4,
                ensure_ascii=False
            )

    except Exception as e:
        logger.exception("jd_analyzer failed")
        state["error"] = f"JD analysis failed: {e}"

    return state
