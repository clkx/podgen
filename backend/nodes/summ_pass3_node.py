from backend.chains.summ_pass3_chain import summ_pass3_chain

def summ_pass3_node(state):
    """take the content and write a third pass summary"""
    print("---THIRD PASS SUMMARY---")
    first_pass_summary = state['first_pass_summary']
    second_pass_summary = state['second_pass_summary']

    third_pass_summary = summ_pass3_chain.invoke({
        "content": state['content'],
        "first_pass_summary": first_pass_summary,
        "second_pass_summary": second_pass_summary
    })

    content = first_pass_summary + second_pass_summary + third_pass_summary

    return {"content": content}