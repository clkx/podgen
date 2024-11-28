from langgraph.graph import StateGraph
from langgraph.constants import START, END

from backend.states import PromptState, PromptInputState, PromptOutputState
from backend.graphs.research_graph import create_research_graph
from backend.graphs.scriptwriting_graph import create_scriptwriting_graph

def topic_to_instruction(state):
    return {"instruction": state["topic"]}

def report_reading_node(state):
    return {"content": state["final_report"]}


def create_prompt_graph():
    research_graph = create_research_graph()
    scriptwriting_graph = create_scriptwriting_graph()

    builder = StateGraph(PromptState, input=PromptInputState, output=PromptOutputState)
    builder.add_node("research_graph", research_graph)
    builder.add_node("report_reading", report_reading_node)
    builder.add_node("scriptwriting_graph", scriptwriting_graph)

    builder.add_edge(START, "research_graph")
    builder.add_edge("research_graph", "report_reading")
    builder.add_edge("report_reading", "scriptwriting_graph")
    builder.add_edge("scriptwriting_graph", END)

    return builder.compile()


if __name__ == "__main__":
    prompt_graph = create_prompt_graph()
    test_topic = "台灣的科技發展"
    test_max_analysts = 3
    test_host_name = "小志"
    test_host_background = "小志是一位資深科技記者，擁有豐富的科技新聞採訪經驗，擅長以輕鬆有趣的方式採訪嘉賓，並將複雜的科技議題轉化為聽眾容易理解的內容。"
    test_guest_name = "大目博士"
    test_guest_background = "大目博士是一位資深的人工智能專家，擁有豐富的人工智能研究經驗，擅長以輕鬆有趣的方式解釋複雜的科技議題，並將其轉化為聽眾容易理解的內容。"
    
    prompt_graph.invoke({"topic": test_topic, "max_analysts": test_max_analysts, "host_name": test_host_name, "guest_name": test_guest_name, "host_background": test_host_background, "guest_background": test_guest_background})

