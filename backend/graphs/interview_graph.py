from langgraph.graph import StateGraph
from backend.states import InterviewState
from backend.nodes.interview_nodes import generate_question_node, generate_answer_node, save_interview_node, route_messages_node
from backend.nodes.search_nodes import search_arxiv_node, search_wikipedia_node, search_web_node
from backend.nodes.write_nodes import write_section_node
from langgraph.constants import START, END
from langchain_core.messages import HumanMessage
from backend.schema import Analyst


def create_interview_graph():
    # Add nodes and edges 
    builder = StateGraph(InterviewState)
    builder.add_node("ask_question", generate_question_node)
    builder.add_node("search_web", search_web_node)
    builder.add_node("search_wikipedia", search_wikipedia_node)
    builder.add_node("search_arxiv", search_arxiv_node)
    builder.add_node("answer_question", generate_answer_node)
    builder.add_node("save_interview", save_interview_node)
    builder.add_node("write_section", write_section_node)

    # Flow
    builder.add_edge(START, "ask_question")
    builder.add_edge("ask_question", "search_web")
    builder.add_edge("ask_question", "search_wikipedia")
    builder.add_edge("ask_question", "search_arxiv")
    builder.add_edge("search_web", "answer_question")
    builder.add_edge("search_wikipedia", "answer_question")
    builder.add_edge("search_arxiv", "answer_question")
    builder.add_conditional_edges("answer_question", route_messages_node,['ask_question','save_interview'])
    builder.add_edge("save_interview", "write_section")
    builder.add_edge("write_section", END)

    interview_graph = builder.compile()

    return interview_graph


if __name__ == "__main__":
    test_analysts = Analyst(affiliation='Tech Innovators Inc.', name='Dr. Emily Carter', role='Technology Analyst', description='Dr. Carter focuses on evaluating emerging technologies and their potential impact on various industries. She is particularly interested in how LangGraph can streamline processes and improve efficiency in tech-driven companies.')
    test_topic = "AI"
    interview_graph = create_interview_graph()
    messages = [HumanMessage(f"So you said you were writing an article on {test_topic}?")]
    thread = {"configurable": {"thread_id": "1"}}
    interview = interview_graph.invoke({"analyst": test_analysts, "messages": messages, "max_num_turns": 2}, thread)
    print(interview['sections'][0])
