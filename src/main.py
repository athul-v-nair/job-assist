import logging
from src.tools.pdf_parser import parse_pdf_from_path
from src.graph.graph import build_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
