from backend.chains.summ_pass2_chain import summ_pass2_chain

def summ_pass2_node(state):
    """take the content and write a second pass summary"""
    print("---SECOND PASS SUMMARY---")

    second_pass_summary = summ_pass2_chain.invoke({
        "content": state['content'],
        "first_pass_summary": state['first_pass_summary']
    })

    return {"second_pass_summary": second_pass_summary}