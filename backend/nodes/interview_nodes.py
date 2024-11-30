from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, get_buffer_string

from backend.models.llm import LLM
from backend.states import GenerateAnalystsState, InterviewState
from backend.schema import Perspectives



def create_analysts_node(state: GenerateAnalystsState):
    """ Create analysts """
    
    topic=state['topic']
    max_analysts=state['max_analysts']
    human_analyst_feedback=state.get('human_analyst_feedback', '')

    analyst_prompt_template="""You are tasked with creating a set of AI analyst personas. Follow these instructions carefully:
    1. First, review the research topic: {topic}
    2. Determine the most interesting themes based upon documents and / or feedback above.             
    3. Pick the top {max_analysts} themes.
    4. Assign one analyst to each theme."""

    system_message = analyst_prompt_template.format(topic=topic, max_analysts=max_analysts)

    structured_llm = LLM.with_structured_output(Perspectives)

    result = structured_llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content="Generate the set of analysts.")])

    # Write the list of analysis to state
    return {"analysts": result.analysts}


def generate_answer_node(state: InterviewState):
    """ Node to answer a question """

    # Get state
    analyst = state["analyst"]
    messages = state["messages"]
    context = state["context"]

    answer_instructions = """You are an expert being interviewed by an analyst.
    Here is analyst area of focus: {goals}.     
    You goal is to answer a question posed by the interviewer.
    To answer question, use this context:
            
    {context}

    When answering questions, follow these guidelines:
    1. Use only the information provided in the context.    
    2. Do not introduce external information or make assumptions beyond what is explicitly stated in the context.
    3. The context contain sources at the topic of each individual document.
    4. Include these sources your answer next to any relevant statements. For example, for source # 1 use [1]. 
    5. List your sources in order at the bottom of your answer. [1] Source 1, [2] Source 2, etc   
    6. If the source is: <Document source="assistant/docs/llama3_1.pdf" page="7"/>' then just list:     
    [1] assistant/docs/llama3_1.pdf, page 7 
    And skip the addition of the brackets as well as the Document source preamble in your citation."""

    # Answer question
    system_message = answer_instructions.format(goals=analyst.persona, context=context)
    answer = LLM.invoke([SystemMessage(content=system_message)]+messages)
            
    # Name the message as coming from the expert
    answer.name = "expert"
    
    # Append it to state
    return {"messages": [answer]}



def generate_question_node(state: InterviewState):
    """ Node to generate a question """

    # Get state
    analyst = state["analyst"]
    messages = state["messages"]


    question_instructions = """You are an analyst tasked with interviewing an expert to learn about a specific topic. 
    Your goal is boil down to interesting and specific insights related to your topic.
    1. Interesting: Insights that people will find surprising or non-obvious.     
    2. Specific: Insights that avoid generalities and include specific examples from the expert.
    Here is your topic of focus and set of goals: {goals}    
    Begin by introducing yourself using a name that fits your persona, and then ask your question.
    Continue to ask questions to drill down and refine your understanding of the topic.    
    When you are satisfied with your understanding, complete the interview with: "Thank you so much for your help!"
    Remember to stay in character throughout your response, reflecting the persona and goals provided to you."""

    # Generate question 
    system_message = question_instructions.format(goals=analyst.persona)
    question = LLM.invoke([SystemMessage(content=system_message)]+messages)
        
    # Write messages to state
    return {"messages": [question]}



def route_messages_node(state: InterviewState, name: str = "expert"):
    """ Route between question and answer """
    
    # Get messages
    messages = state["messages"]
    max_num_turns = state.get('max_num_turns',3)

    # Check the number of expert answers 
    num_responses = len(
        [m for m in messages if isinstance(m, AIMessage) and m.name == name]
    )

    # End if expert has answered more than the max turns
    if num_responses >= max_num_turns:
        return 'save_interview_node'

    # This router is run after each question - answer pair 
    # Get the last question asked to check if it signals the end of discussion
    last_question = messages[-2]
    
    if "Thank you so much for your help" in last_question.content:
        return 'save_interview_node'
    return "generate_question_node"



def save_interview_node(state: InterviewState):
    """ Save interviews """

    # Get messages
    messages = state["messages"]
    
    # Convert interview to a string
    interview = get_buffer_string(messages)
    
    # Save to interviews key
    return {"interview": interview}