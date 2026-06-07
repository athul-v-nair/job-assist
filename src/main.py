import logging
from src.tools.pdf_parser import parse_pdf_from_path
from langgraph.graph import StateGraph, START, END
from src.graph.state import JobAssistAgentState

from src.nodes.analyzer import resume_jd_analyzer_node
from src.nodes.rewriter import resume_rewriter_node
from src.nodes.rescorer import rescorer_node
from src.nodes.roadmap import roadmap_node
from src.nodes.interview_prep import interview_prep_node

from src.config.config import get_settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

def route_after_score(state: JobAssistAgentState) -> str:
    """
    Conditional edge after score.

    Shared routing function — used by both conditional edges:
        - after resume_jd_analyzer  (reads baseline scores)
        - after rescorer             (reads improved scores)

    Caller controls which scores are passed in via ats_score / match_percentage,

    Proceeds to END once BOTH thresholds are met, or the cap is hit
    (so we don't loop forever on a weak resume).
    """
    iteration = state.get("iteration", 0)
    ats_score = state.get("improved_ats_score") or state.get("baseline_ats_score", 0)
    match_percentage = state.get("improved_match_percentage") or state.get("baseline_match_percentage", 0)
    error = state.get("error")

    # Importing config variables
    ATS_THRESHOLD = settings.ATS_THRESHOLD
    MATCH_THRESHOLD = settings.MATCH_THRESHOLD
    MAX_ITERATIONS = settings.MAX_ITERATIONS

    # Always stop on error
    if error:
        logger.warning("route_after_rescorer: error in state — stopping. error: %s", error)
        return END

    thresholds_met = ats_score >= ATS_THRESHOLD and match_percentage >= MATCH_THRESHOLD

    if thresholds_met:
        logger.info(
            "route_after_rescorer: thresholds met (ATS: %d >= %d, match: %d%% >= %d%%) — proceeding to END",
            ats_score, ATS_THRESHOLD, match_percentage, MATCH_THRESHOLD,
        )
        return "roadmap"

    if iteration >= MAX_ITERATIONS:
        logger.warning(
            "route_after_rescorer: max iterations (%d) reached — stopping. "
            "Best scores: ATS %d, match %d%%",
            MAX_ITERATIONS, ats_score, match_percentage,
        )
        return "roadmap"

    # Increment iteration counter before looping back
    state["iteration"] = iteration + 1
    logger.info(
        "route_after_rescorer: thresholds NOT met (ATS: %d, match: %d%%) — "
        "looping back to rewriter (iteration %d → %d)",
        ats_score, match_percentage, iteration, state["iteration"],
    )
    return "resume_rewriter"


def build_graph():
    # Creating a graph
    graph = StateGraph(JobAssistAgentState)

    # Register Nodes
    graph.add_node('resume_jd_analyzer', resume_jd_analyzer_node)
    graph.add_node('resume_rewriter', resume_rewriter_node)
    graph.add_node('rescorer', rescorer_node)
    graph.add_node('roadmap', roadmap_node)
    graph.add_node('interview_prep', interview_prep_node)

    # ----------------
    # Adding the edges
    # ----------------

    graph.add_edge(START, 'resume_jd_analyzer')

    # After analyzer: if baseline already meets threshold → END, else → rewriter
    graph.add_conditional_edges(
        "resume_jd_analyzer",
        route_after_score,
        {
            "resume_rewriter": "resume_rewriter",
            "roadmap": "roadmap"
        },
    )

    graph.add_edge('resume_rewriter', 'rescorer')
    
    # After rescorer: if improved scores meet threshold → END, else → rewriter (loop)
    graph.add_conditional_edges(
        "rescorer",
        route_after_score,
        {
            "resume_rewriter": "resume_rewriter",
            "roadmap": "roadmap"
        },
    )

    graph.add_edge('roadmap', 'interview_prep')
    graph.add_edge('interview_prep', END)

    return graph.compile()


if __name__ == '__main__':
    # Setting up the inputs -> dev testing
    try:
        resume_data = parse_pdf_from_path('data/resume.pdf') # change this to load directly from file
        with open('data/job_desc.txt', 'r') as f:
            job_description = f.read()
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")

    # Initial state
    initial_state = {
        "resume_text": resume_data,
        "job_description": job_description,
        "status": "starting the workflow",
        "error": None,
    }

    workflow = build_graph()

    # Displaying the graph
    print(workflow.get_graph().draw_ascii())

    # Run the workflow
    result = workflow.invoke(initial_state)
