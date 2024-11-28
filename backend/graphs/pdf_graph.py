from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import List

from backend.nodes.pdf_reading_node import pdf_reading_node
from backend.graphs.summarizing_graph import create_summarizing_graph
from backend.graphs.scriptwriting_graph import create_scriptwriting_graph


class PdfInputState(TypedDict):
    pdf_path : str
    host_name : str
    guest_name : str
    host_background : str
    guest_background : str


class PdfState(TypedDict):
    pdf_path : str
    content : str
    dialogue : List[dict]
    host_name : str
    guest_name : str
    host_background : str
    guest_background : str


class PdfOutputState(TypedDict):
    dialogue : List[dict]
    host_name : str
    guest_name : str
    host_background : str
    guest_background : str


def create_pdf_graph():
    """
    由 PDF 路徑生成對話腳本
    """
    builder = StateGraph(PdfState, input=PdfInputState, output=PdfOutputState)
    summarizing_graph = create_summarizing_graph()
    scriptwriting_graph = create_scriptwriting_graph()

    # Add nodes
    builder.add_node("pdf_reading_node", pdf_reading_node)
    builder.add_node("summarizing_graph", summarizing_graph)
    builder.add_node("scriptwriting_graph", scriptwriting_graph)

    # Add edges
    builder.add_edge(START, "pdf_reading_node")
    builder.add_edge("pdf_reading_node", "summarizing_graph")
    builder.add_edge("summarizing_graph", "scriptwriting_graph")
    builder.add_edge("scriptwriting_graph", END)

    return builder.compile()

if __name__ == "__main__":

    pdf_graph = create_pdf_graph()
    result = pdf_graph.invoke(
        {"pdf_path": r"backend\stores\temp\20241125_131213\20241125_131213_original.pdf",
         "host_name": "柯南",
         "guest_name": "阿笠博士",
         "host_background": "柯南是一位資深的領域學者，擁有豐富的研究經驗，擅長以輕鬆有趣的方式採訪嘉賓，並將複雜的議題轉化為聽眾容易理解的內容。",
         "guest_background": "阿笠博士是一位資深的領域學者，擁有豐富的研究經驗，擅長以輕鬆有趣的方式解釋複雜的議題，並將其轉化為聽眾容易理解的內容。"}
    )
    print(result)