# rag_prompt = PromptTemplate(
#     template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
#     You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.\n

#      <|eot_id|><|start_header_id|>user<|end_header_id|>
#     QUESTION: {question} \n
#     CONTEXT: {context} \n
#     Answer:
#     <|eot_id|>
#     <|start_header_id|>assistant<|end_header_id|>
#     """,
#     input_variables=["question","context"],
# )

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool

from langgraph.prebuilt import ToolNode
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.llm import llm



# rag_template = """你是一位優秀的Podcast腳本家，總是能夠針對客戶的要求撰寫出輕鬆有趣且引人入勝的Podcast腳本，
# 而現在你接到了以下的Podcast腳本撰寫案件，但在正式開始撰寫Podcast腳本前，你必須先依據客戶的要求收集撰寫這個Podcast腳本時所需要的背景資料。

# 背景資料收集原則:
# - 

# 客戶對Podcast主題的要求:
# {instruction}

# 你目前所調查到的背景資料:
# {content}"""

from langgraph.graph import StateGraph, MessagesState, START, END


# The function name, type hints, and docstring are all part of the tool
# schema that's passed to the model. Defining good, descriptive schemas
# is an extension of prompt engineering and is an important part of
# getting models to perform well.
@tool
def add(a: int, b: int) -> int:
    """Add two integers.

    Args:
        a: First integer
        b: Second integer
    """
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers.

    Args:
        a: First integer
        b: Second integer
    """
    return a * b

tool_prompt = ChatPromptTemplate([
    ('user', "{question}")
])

tools = [add, multiply]

llm_with_tools = llm.bind_tools(tools)

tool_chain = tool_prompt | llm_with_tools


# class RAGState(MessagesState):
#     messages : List[BaseMessage]

tool_node = ToolNode(tools)


def should_continue_node(state):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END


def agent_node(state):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

workflow = StateGraph(MessagesState)

# Define the two nodes we will cycle between
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue_node, ["tools", END])
workflow.add_edge("tools", "agent")

app = workflow.compile()

## For testing
if __name__ == "__main__":
    result = app.invoke({"question": "who is the president of Taiwan?"})
    print(result)


    # tool_calls = tool_chain.invoke({"question": "what is the result of 5*(4 + 3)?"}).tool_calls
    tool_calls = tool_chain.invoke({"question": "who is the president of Taiwan?"})
    print(tool_calls)
