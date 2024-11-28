from backend.chains.write_chain import write_chain

def writing_node(state):
    """take the initial prompt and write a plan to make a long doc"""
    print("---WRITING THE SCRIPT---")

    dialogue = state.get('dialogue', [])
    plan = state['plan']

    for subplan in plan:
        # Invoke the write_chain
        result = write_chain.invoke({
            "instruction": state.get('instruction', '請根據背景知識所提供的論文內容，非常深入的探討論文的技術內容，以幫助聽眾完全理解論文的內容，盡量引用論文中的數據或是其論點'),
            "title": state['title'],
            "plan": plan,
            "dialogue": dialogue,
            "subplan_num": subplan['subplan_num'],
            "host_name": state.get('host_name', '主持人'),
            "host_background": state.get('host_background', '主持人是一位資深的領域學者，擁有豐富的研究經驗，擅長以輕鬆有趣的方式採訪嘉賓，並將複雜的議題轉化為聽眾容易理解的內容。'),
            "guest_name": state.get('guest_name', '來賓'),
            "guest_background": state.get('guest_background', '來賓是一位資深的領域學者，擁有豐富的研究經驗，擅長以輕鬆有趣的方式解釋複雜的議題，並將其轉化為聽眾容易理解的內容。'),
            "content": state['content']
        })
        
        dialogue += result['dialogue']

    return {"dialogue": dialogue}



