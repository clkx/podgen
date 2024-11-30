from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

from backend.nodes.summarize_nodes import summ_pass1_node, summ_pass2_node, summ_pass3_node


class SummarizingInputState(TypedDict):
    content : str
    host_name : str
    guest_name : str
    host_background : str
    guest_background : str

class SummarizingState(TypedDict):
    first_pass_summary : str
    second_pass_summary : str
    content : str
    host_name : str
    guest_name : str
    host_background : str
    guest_background : str

class SummarizingOutputState(TypedDict):
    content : str
    host_name : str
    guest_name : str
    host_background : str
    guest_background : str


def create_summarizing_graph():
    """
    生成摘要
    """
    builder = StateGraph(SummarizingState, input=SummarizingInputState, output=SummarizingOutputState)

    # Add nodes
    builder.add_node("summ_pass1_node", summ_pass1_node)
    builder.add_node("summ_pass2_node", summ_pass2_node)
    builder.add_node("summ_pass3_node", summ_pass3_node)

    # Add edges
    builder.add_edge(START, "summ_pass1_node")
    builder.add_edge("summ_pass1_node", "summ_pass2_node")
    builder.add_edge("summ_pass2_node", "summ_pass3_node")
    builder.add_edge("summ_pass3_node", END)

    return builder.compile()


if __name__ == "__main__":
    summarizing_workflow = create_summarizing_graph()
    test_content = """Taiwan-Llama 系列模型過去資訊
    台大林彥廷博士在去年的時間，以 Llama 2 模型，以及相關的繁體中文資源，Fine-Tune 了相關的繁體中文 LLM 模型，命名為 Taiwan-Llama 模型，當時成為台灣第一個釋出的繁體中文大型語言開源模型，也讓不少企業試著研究是否能夠導入到專案之中。
    而在 2024 年， Meta 出了 Llama 3 之後，台灣相關開源模型的單位也在著手準備相關模型的 Fine-Tune ，而本次文章，我將整理由林彥廷與其他合作團隊所開源出來的 Llama-3-Taiwan 模型，讓大家能夠更清楚此次模型，目前能力已經能夠到達什麼程度。
    II. Llama-3-Taiwan 模型介紹
    1. 模型名稱
    Llama-3-Taiwan 系列模型
    此模型是透過 Meta 所開源 Llama-3 模型，並且在規範下進行繁體中文語料庫 Fine-Tuning ，所製作出來的繁體中文開源 LLM 模型。

    2. 模型開源狀況 / License
    根據 Llama-3 許可證發布的開放模型

    3. 參數量
    8B、70B

    4. 開源型態
    本次 Llama-3-Taiwan 模型一共開源了以下三種模型型態，並且一併提供相關 HuggingFace 連結，你可以進到 Huggingface 申請後，取得模型並使用它：

    Instruct Version
    yentinglin/Llama-3-Taiwan-8B-Instruct
    yentinglin/Llama-3-Taiwan-70B-Instruct
    Verbose Version
    yentinglin/Llama-3-Taiwan-8B-Instruct-DPO
    yentinglin/Llama-3-Taiwan-70B-Instruct-DPO
    Long-context Version
    yentinglin/Llama-3-Taiwan-8B-Instruct-128k
    yentinglin/Llama-3-Taiwan-70B-Instruct-128k
    [ 非官方 ] GGUF 模型
    ccpl17/Llama-3-Taiwan-8B-Instruct-GGUF
    4.1. 什麼是 DPO (Direct Preference Optimization) 模型？

    在說明什麼是 DPO 之前，我們先來了解一下什麼是 PPO（Proximal Policy Optimization），因為標準的 RLHF Fine-Tuning 背後使用的就是 PPO 技術。

    如果我們以棒球比賽來舉例，打擊者必須學習如何才能獲得最高分，而 PPO 就像是一位總教練。它會根據你的當前狀態，告訴你應該採取什麼動作才能獲得最佳結果。當你按照教練的建議去做時，你會得到一些分數（獎勵），教練也會根據你獲得的分數來調整建議，讓你下次表現得更好。

    PPO 會設法平衡學習新技巧與堅持已經學到的好技巧之間的關係。它不希望你的策略變化太快，以避免學到一些壞策略，這就像教練想要確保你不會因為嘗試新動作而忘記基本技巧。

    接下來，我們來說明 DPO。DPO 技術主要是希望能夠優化人類偏好，但同時不需要使用強化學習。相比於 PPO，DPO 直接優化最能滿足偏好的策略，使用簡單的分類目標，透過數據來建立一個獎勵模型，這個模型可以預測或評估行動的價值（即獎勵），而不需要明確地定義每個行動的具體獎勵，就類似於棒球數據科學那樣，根據每個人的狀態擬定出場上的最優策略。

    Llama-3-Taiwan 使用 Feedback Direct Preference Optimization（FDPO）模式來進行處理。這種方法的核心在於直接利用用戶的反饋來指導模型的優化過程，從而提升模型的適用性和效果。

    一般的 Direct Preference Optimization（DPO）通常依賴於已經存在的偏好數據或評分，這些數據可能是歷史數據或預先收集的偏好樣本。而 Feedback DPO 主要依靠實時或動態的用戶反饋，這些反饋可以是用戶在使用過程中提供的即時數據。
    5. 資料來源
    根據之前在許多地方的分享會上，林彥廷就有多次方想到，製作此模型時，Project TAME 團隊一直遇到：
    1. 資料不足問題，本土資料很珍貴。
    2. 資料品質不足，需要各領域專家進行認證作業。
    為了解決這個問題，Project TAME 團隊採用聚集各領域專家、提供相關資料的模式，來因應資料不足的挑戰。而這些資料來源，包括了占所有訓練資料三分之一的合成資料（如合成教科書內容等），約1,000億Token左右，以及其他來自媒體、石化、法律、醫療、化工、製造業製程、遊戲等資料，包括來自網頁、社群平臺、資料庫、書籍、程式碼等。
    6.4. 看完上述的測試後，我們可以看到

    在「台灣化」這件事情上，的確 Llama-3-Taiwan 模型表現的比其他模型來的更好，主要會有這樣的現象，也是因為林彥廷團隊有針對台灣的知識點和內容進行處理，讓知識能夠盡可能地回答出來。
    此模型是基於 Llama 3 進行 Fine-Tune 的情形下，因此在架構不變下，不會有突破性的進步，但一定會比原始的模型來的好。
    按照此次分享的內容，如果企業想針對企業的各領域知識進行 Fine-Tune ，能夠讓模型更認識台灣的語言與知識內容。
    """
    print(summarizing_workflow.invoke({"content": test_content}))

