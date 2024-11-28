from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from backend.models.llm import llm


write_template = """你是一位優秀的Podcast腳本家，總是能夠針對客戶的要求撰寫出輕鬆有趣且引人入勝的Podcast腳本，
而現在你接到了一份名為{title}的Podcast腳本撰寫案件，並且你先前已經撰寫了一份詳細的Podcast腳本大綱如下，請你接著撰寫Podcast腳本各個段落的對話腳本。

客戶要求:
務必要嚴格遵守的podcast腳本撰寫規範
{instruction}

背景資料:
請利用此處提供的背景資料，撰寫Podcast腳本各個段落的對話腳本
{content}

Podcast腳本大綱:
{plan}

你先前已經撰寫的Podcast腳本對話腳本如下:
{dialogue}

你現在要撰寫的Podcast腳本段落是: {subplan_num}

Podcast參與者的背景資料(只有這兩位參與者，沒有別的來賓):
主持人{host_name}: {host_background}
嘉賓{guest_name}: {guest_background}

撰寫原則:
- 依據客戶需求、客戶所提供的背景資料以及Podcast腳本大綱，接續撰寫第{subplan_num}段的對話腳本，包含主持人{host_name}和嘉賓{guest_name}的對話。
- 風格以輕鬆有趣，並且能夠吸引聽眾的注意力為主。
- 請確保每個段落清楚明確。將內容分成必要的段落數量，每個段落專注於一個獨特的主題面向。
- 確保所有段落涵蓋整個Podcast腳本的客戶需求以及客戶所提供的背景資料。除非特別要求，否則避免開放式的結論或修辭性的引導。

對話規則:
- 段落的劃分僅是為了撰寫方便，實際上整個Podcast腳本是一個連續的對話，以整體的流暢性為主。
- 除非目前的段落為結尾段(最後一段)，否則預設對話會持續進行，不要在段落結束時進行結論，也不要做出任何對後續段落期待性的敘述。
- 若目前段落為第一段，則以有吸引力的開場引起觀眾注意。
- 每個段落至少包含20組對話，總共至少40行對話腳本。
- 同時也應該接續先前的對話撰寫此段落的對話腳本。
- 始終由主持人{host_name}發起對話並採訪來賓{guest_name}。
- 融入自然的口語化的模式，包括偶爾的語氣詞（例如：「嗯」、「欸」、「喔」）。
- 展現真實的好奇或驚訝時刻。
- 來賓在表達複雜想法時可能有短暫的卡頓。
- 主持人{host_name}和嘉賓{guest_name}的對話應該是互動且有趣的，適時加入輕鬆或幽默的片段，避免單方面的獨白。
- 隨著對話進行逐步增加深度與複雜性。
- 包含短暫的「喘息」時刻，讓觀眾有時間消化複雜資訊。"""



write_prompt = ChatPromptTemplate([
    ('user', write_template)
])

class DialogueLine(BaseModel):
    """對話腳本中的其中一組對話，說話者必須為主持人或嘉賓其中一人，並且包含說話者的名稱與其對話內容"""
    speaker: str = Field(description="說話者的名字")
    content: str = Field(description="說話內容")

class DialogueScript(BaseModel):
    """組成本次Podcast的全部對話腳本，包含主持人與嘉賓的多組對話，這些對話應該是連續的"""
    dialogue: list[DialogueLine] = Field(description="對話腳本")


def object_to_dict(obj):
    return obj.model_dump()

structured_llm = llm.with_structured_output(DialogueScript)
# Create the write chain
write_chain = write_prompt | structured_llm | object_to_dict

if __name__ == "__main__":
    test_instruction = "用惡搞的方式來撰寫"
    test_title = "Taiwan-Llama 的有趣發展史"
    test_plan = """[{'segment': '第一段', 'main_topic': '模型的歷史淵源', 'summary': '介紹 Lin Yenting 博士如何在去年成功 Fine-Tune Llama 2 模型，創造出台灣首個繁體中文開源大型語言模型 Taiwan-Llama，以及這一成就對於企業和研究的影響與啟示。'}, {'segment': '第二段', 'main_topic': '全新登場：Llama-3-Taiwan 模型', 'summary': '深入探討 Llama-3-Taiwan 模型的背景，包括其名稱來源、開源狀況及參數量，並以輕鬆幽默的方式解釋模型的開發過程。'}, {'segment': '第三段', 'main_topic': '什麼是 DPO？', 'summary': '用球賽比喻來解釋 DPO（Direct Preference Optimization）技術，並介紹其相對於 PPO 的優點，輕鬆幽默地展示如何利用用戶反饋來提升模型表現。'}, {'segment': '第四段', 'main_topic': '資料來源與處理挑戰', 'summary': '探討 Project TAME 團隊在製作模型時所面對的資料不足問題，分享他們如何通過專家合作及合成資料來克服這些挑戰，並用了一些搞笑的比喻來吸引聽眾。'}, {'segment': '第五段', 'main_topic': '模型的交付與未來展望', 'summary': '總結 Llama-3-Taiwan 模型在台灣化方面的優越性能，並幽默地討論企業如何利用這個模型進行 Fine-Tuning，以利於未來的發展和應用場景。'}, {'segment': '結尾段', 'main_topic': '模型小結與感謝', 'summary': '回顧整集的內容，以輕鬆的方式鼓勵聽眾進一步了解台湾的智慧科技發展，並感謝 Lin Yenting 及其團隊的貢獻，鼓舞大家持續探索人工智能的可能性。'}]}"""
    test_dialogue = [{'小志': '歡迎大家回到我們的Podcast節目！今天我們要探討的主題可謂是台灣科技界的一個驚天大消息！就是林彥廷博士成功地將Llama 2模型進行了Fine-Tune，創造出了繁體中文的開源大型語言模型，Taiwan-Llama！這不僅是技術上的突破，更是在台灣科技史上的一個里程碑！'}, {'大目博士': '對啊，Taiwan-Llama還真是個難以置信的成就！想想看，台灣竟然能在這麼短的時間內推出一個開源語言模型，還是首個繁體中文的呢！'}, {'小志': '我聽起來就像是一部科幻電影的情節！欸，大目博士，你能幫我們聊聊，這個Taiwan-Llama對於企業和研究的影響究竟有多大嗎？'}]
    test_subplan_num = "第二段"
    test_host = "小志"
    test_host_background = "小志是一位資深科技記者，擁有豐富的科技新聞採訪經驗，擅長以輕鬆有趣的方式採訪嘉賓，並將複雜的科技議題轉化為聽眾容易理解的內容。"
    test_guest = "大目博士"
    test_guest_background = "大目博士是一位資深的人工智能專家，擁有豐富的人工智能研究經驗，擅長以輕鬆有趣的方式解釋複雜的科技議題，並將其轉化為聽眾容易理解的內容。"

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


    # Invoke the write_chain
    result = write_chain.invoke({
        "instruction": test_instruction,
        "title": test_title,
        "plan": test_plan,
        "dialogue": [],
        "subplan_num": test_subplan_num,
        "host_name": test_host,
        "guest_name": test_guest,
        "host_background": test_host_background,
        "guest_background": test_guest_background,
        "content": test_content
    })
    
    # Print the result
    print("Generated Paragraph:")
    print(result)
