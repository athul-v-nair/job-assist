from langgraph.graph import StateGraph, START, END
from src.graph.state import JobAssistAgentState

# mock functions
def resume_jd_analyzer_node():
    pass
def scorer_node():
    pass
def resume_rewriter_node():
    pass
def rescorer_node():
    pass
def self_reflection_node():
    pass
def preparation_helper_node():
    pass
def feedback():
    pass

def build_graph():
    graph = StateGraph(JobAssistAgentState)

    # Register Nodes
    graph.add_node('resume_jd_analyzer', resume_jd_analyzer_node)
    graph.add_node('scorer', scorer_node)
    graph.add_node('resume_rewriter', resume_rewriter_node)
    graph.add_node("rescorer", rescorer_node)
    graph.add_node("self_reflection", self_reflection_node)
    graph.add_node("preparation_helper", preparation_helper_node)

    # Adding the edges
    graph.add_edge(START, 'resume_jd_analyzer')
    graph.add_edge('resume_jd_analyzer', 'scorer')
    graph.add_edge('scorer', 'resume_rewriter')
    graph.add_edge('resume_rewriter', 'rescorer')

    graph.add_conditional_edges('rescorer', feedback, {
        'reject': 'self_reflection',
        'accept': 'preparation_helper'
    })

    graph.add_edge('self_reflection', 'resume_rewriter')
    graph.add_edge('preparation_helper', END)

    workflow = graph.compile()

    # checking the workflow
    print(workflow.get_graph().draw_ascii())