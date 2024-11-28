from langgraph.graph import MessagesState
from typing import  Annotated, List
from typing_extensions import TypedDict
import operator
from backend.schema import Analyst

class GenerateAnalystsState(TypedDict):
    topic: str # Research topic
    max_analysts: int # Number of analysts
    human_analyst_feedback: str # Human feedback
    analysts: List[Analyst] # Analyst asking questions


class InterviewState(MessagesState):
    max_num_turns: int # Number turns of conversation
    context: Annotated[list, operator.add] # Source docs
    analyst: Analyst # Analyst asking questions
    interview: str # Interview transcript
    sections: list # Final key we duplicate in outer state for Send() API

class ResearchGraphState(TypedDict):
    topic: str # Research topic
    max_analysts: int # Number of analysts
    human_analyst_feedback: str # Human feedback
    analysts: List[Analyst] # Analyst asking questions
    sections: Annotated[list, operator.add] # Send() API key
    introduction: str # Introduction for the final report
    content: str # Content for the final report
    conclusion: str # Conclusion for the final report
    final_report: str # Final report


class PromptInputState(TypedDict):
    topic : str
    max_analysts : int
    host_name : str
    guest_name : str
    host_background : str
    guest_background : str


class PromptState(ResearchGraphState):
    topic : str
    instruction : str
    content : str
    host_name : str
    guest_name : str
    host_background : str
    guest_background : str


class PromptOutputState(TypedDict):
    dialogue : List[dict]
    host_name : str
    guest_name : str
    host_background : str
    guest_background : str