from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage
from langgraph.constants import Send

from backend.states import ResearchGraphState
from backend.graphs.interview_graph import create_interview_graph
from backend.nodes.interview_nodes import create_analysts_node
from backend.nodes.write_nodes import write_report_node, write_introduction_node, write_conclusion_node, finalize_report_node


def initiate_all_interviews(state: ResearchGraphState):
    """ This is the "map" step where we run each interview sub-graph using Send API """    
    topic = state["topic"]
    return [Send("conduct_interview", {"analyst": analyst,
                                       "messages": [HumanMessage(content=f"So you said you were writing an article on {topic}?")]}) for analyst in state["analysts"]]


def create_research_graph():
    interview_graph = create_interview_graph()

    builder = StateGraph(ResearchGraphState)
    builder.add_node("create_analysts", create_analysts_node)
    builder.add_node("conduct_interview", interview_graph)
    builder.add_node("write_report",write_report_node)
    builder.add_node("write_introduction",write_introduction_node)
    builder.add_node("write_conclusion",write_conclusion_node)
    builder.add_node("finalize_report",finalize_report_node)

    builder.add_edge(START, "create_analysts")
    builder.add_conditional_edges("create_analysts", initiate_all_interviews, ["conduct_interview"])
    builder.add_edge("conduct_interview", "write_report")
    builder.add_edge("conduct_interview", "write_introduction")
    builder.add_edge("conduct_interview", "write_conclusion")
    builder.add_edge(["write_conclusion", "write_report", "write_introduction"], "finalize_report")
    builder.add_edge("finalize_report", END)

    research_graph = builder.compile()
    return research_graph

if __name__ == "__main__":
    research_graph = create_research_graph()
    test_max_analysts = 3 
    test_topic = "The benefits of adopting LangGraph as an agent framework"
    research_graph.invoke({"topic": test_topic, "max_analysts": test_max_analysts})

