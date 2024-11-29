from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from backend.models.llm import LLM


summ_pass3_template = """You have already performed a first and second pass on this paper with the following summaries:

    First Pass:
    {first_pass_summary}

    Second Pass:
    {second_pass_summary}

    Now, perform a third pass read of the paper. Your goal is to virtually re-implement the paper:
    1. Identify and challenge every assumption in every statement
    2. Think about how you would present each idea
    3. Jot down ideas for future work

    Provide a detailed analysis including:
    1. The entire structure of the paper
    2. Its strong and weak points
    3. Implicit assumptions
    4. Missing citations to relevant work
    5. Potential issues with experimental or analytical techniques

    Paper content:
    {content}

    Analysis:"""

summ_pass3_prompt = ChatPromptTemplate([
    ('user', summ_pass3_template)
])

summ_pass3_chain = summ_pass3_prompt | LLM | StrOutputParser()

## For testing
if __name__ == "__main__":

    test_first_pass_summary = """**First Pass Read:**

1. **Title, Abstract, and Introduction**: The paper is about the Taiwan-Llama model series, detailing the development of a fine-tuned large language model (LLM) based on Meta's Llama 3. It outlines previous work by Dr. Lin Yenting and his team on the Llama 2 model and the evolution into Llama-3-Taiwan. The goal of the paper appears to be informing readers about the capabilities and characteristics of the Taiwan-specific model.

2. **Section and Sub-section Headings**: 
   - The paper is organized into clear sections that detail:
     - Introduction of Llama-3-Taiwan model
     - Model names, open-source status, parameter sizes, and types
     - Explanation of Direct Preference Optimization (DPO) and its application in Llama-3-Taiwan
     - Data source challenges faced during development
     - A concluding performance evaluation of the model's responses to Taiwan-specific inquiries.

3. **Conclusions**: The paper concludes that while the Llama-3-Taiwan model does not significantly redefine foundational models, it demonstrates improved performance in responding to Taiwan-specific knowledge queries due to targeted fine-tuning.

4. **References (noted ones)**: The paper references the original Llama model and the Proximal Policy Optimization (PPO) algorithm, both of which are well-known in the machine learning community. No specific titles of references were provided to review, but references to Llama 2 and Llama 3 are recognized and significant in this context.

---

**Answers to Questions:**

1. **Category**: This paper is a technical report/documentation focused on the development and capabilities of a specific machine learning model — the Taiwan-Llama 3 model.

2. **Context**: This paper is related to prior work with Llama 2 and Llama 3, building on the foundational techniques used in large language models including fine-tuning approaches like PPO (Proximal Policy Optimization) and DPO (Direct Preference Optimization). The theoretical bases lie in reinforcement learning and its adaptation for language models.

3. **Correctness**: The assumptions about using DPO for optimizing model performance and the need for localized, high-quality data appear to be valid based on the context of LLM development, where domain-specific fine-tuning is generally understood to improve model relevance and accuracy.

4. **Contributions**: The paper’s main contributions include the introduction of the Llama-3-Taiwan model, its specific adaptations for the Taiwanese context, and a detailed explanation of the challenges and solutions regarding data sourcing and fine-tuning. It helps enrich the understanding of how tailored models can perform better in specific cultural or regional contexts.

5. **Clarity**: The paper is reasonably well written, with a structured format that aids comprehension. It effectively communicates the technical aspects of the model while being accessible to those familiar with machine learning concepts. More technical jargon could be defined better for clarity, especially for a broader audience outside the immediate field."""
    
    test_second_pass_summary = """**Second Pass Read Summary:**

1. **Thrust of the Paper**: The paper discusses the Taiwan-Llama 3 model, which represents a localized adaptation of the Llama 3 model by fine-tuning it with traditional Chinese data specific to Taiwan. The author aims to highlight the model's capabilities, challenges faced during its development, and its performance on Taiwan-specific knowledge queries. The fine-tuning process, particularly through Direct Preference Optimization (DPO), is a focal point, illustrating how the model was tailored to handle Taiwan-related inquiries more effectively than prior models.

2. **Supporting Evidence**:
   - The introduction of the Llama-3-Taiwan model is explicitly detailed, including configurations such as the available model sizes (8 billion and 70 billion parameters).
   - The paper provides concrete examples of the model versions released on HuggingFace, showcasing its accessibility for further experimentation by other researchers or developers.
   - The explanation of DPO and its relationship to traditional approaches like Proximal Policy Optimization (PPO) illustrates the methodological advancements that underpin the model's training process.
   - The challenges of sourcing quality data for training—the scarcity of local data and the necessity for expert curation—are expressly recognized, with the authors describing their approach to overcoming these challenges by aggregating subject-specific expertise and using synthetic data.

3. **Figures and Diagrams**: There were no specific figures or visual diagrams mentioned in the text provided. However, any such visuals would likely elucidate the architecture of the model, the training pipeline, or comparative performance metrics against other models. If present, I would recommend a careful examination of any charts or diagrams related to metrics of performance, training data distributions, or model architecture for better understanding.

4. **Difficult Parts**: 
   - **Understanding DPO**: The explanation of DPO relative to PPO requires a background understanding of reinforcement learning concepts. While the paper provides a metaphor comparing PPO to a baseball coach, transitioning from this analogy to the technical details of DPO (particularly Feedback DPO) might still be dense without foundational knowledge of RLHF (Reinforcement Learning from Human Feedback).
   - **Data Sourcing Challenges**: The discussion around the challenges in obtaining locally relevant datasets could benefit from deeper examples or clearer definitions of what constitutes "sufficient quality" or "local relevance." The methodology of utilizing both real and synthetic data and how successfully they synergize remains somewhat underexplained.

5. **References**: It would be prudent to mark the following for further reading:
   - Studies or articles on Proximal Policy Optimization (PPO) to understand its role in reinforcement learning and model training.
   - Literature on Direct Preference Optimization (DPO) for insights into how it diverges from traditional reinforcement learning approaches.
   - Research surrounding fine-tuning strategies for large language models specifically within non-English contexts or specialized domains.

By thoroughly analyzing various sections of the paper, it presents a compelling overview of how the Llama-3-Taiwan model is a significant advancement for Taiwan-specific applications while also contributing to the broader field of machine learning through its methodological approaches. Further inquiries into referenced literature would enhance comprehension of the technical details and comparative model assessments.
    """
    
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
    print(summ_pass3_chain.invoke({"first_pass_summary": test_first_pass_summary, "second_pass_summary": test_second_pass_summary, "content": test_content}))