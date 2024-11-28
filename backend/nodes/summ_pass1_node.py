
from backend.chains.summ_pass1_chain import summ_pass1_chain

def summ_pass1_node(state):
    """take the content and write a first pass summary"""
    print("---FIRST PASS SUMMARY---")

    first_pass_summary = summ_pass1_chain.invoke({
        "content": state['content']
    })

    return {"first_pass_summary": first_pass_summary}