from langgraph.constants import END

from backend.states import GenerateAnalystsState

def human_feedback_node(state: GenerateAnalystsState):
    """ No-op node that should be interrupted on """
    pass

def should_continue_node(state: GenerateAnalystsState):
    """ Return the next node to execute """

    # Check if human feedback
    human_analyst_feedback=state.get('human_analyst_feedback', None)
    if human_analyst_feedback:
        return "create_analysts"
    
    # Otherwise end
    return END