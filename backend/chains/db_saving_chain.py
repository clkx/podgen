from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from backend.models.llm import LLM  
# from backend.database.chroma_manager import ChromaDBManager

# vectordb = ChromaDBManager()

# document for test
docs = open(r"C:\Users\k123k\Desktop\podgen\backend\test.txt", "r", encoding="utf-8").read()

print(docs)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=400,
    length_function=len,
    is_separator_regex=False,
    separators=[
        "\n\n",
        "\n",
        " ",
        ".",
        ",",
        "\u200b",  # Zero-width space
        "\uff0c",  # Fullwidth comma
        "\u3001",  # Ideographic comma
        "\uff0e",  # Fullwidth full stop
        "\u3002",  # Ideographic full stop
        "",
    ],
)


texts = text_splitter.split_text(docs)

for text in texts:
    print("==========\n", text)
# print(texts)




HF_EMBEDDING_MODEL = 'BAAI/bge-m3'
hf_embeddings = HuggingFaceEmbeddings(
    model_name=HF_EMBEDDING_MODEL,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': False}
)


vectordb = FAISS.from_texts(texts, hf_embeddings)



# custom_prompt_template = """
# <your system instruction>
# {context}
# Question: {question}
# Helpful Answer:"""


# CUSTOMPROMPT = PromptTemplate(
#     template=custom_prompt_template, input_variables=["context", "question"]
# )
# retriever = vectordb.as_retriever(search_type="similarity",
#     search_kwargs={"k": 100}) # K1, Top100 Snippets
# compressor = FlashrankRerank(model=RERANK_MODEL, top_n=5) # K2, Top5 Answers
# compression_retriever = ContextualCompressionRetriever(
#     base_compressor=compressor, base_retriever=retriever
# )
# qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", 
#     retriever=compression_retriever, return_source_documents=True)
# ## Inject custom prompt 
# qa.combine_documents_chain.llm_chain.prompt = CUSTOMPROMPT
# question = "<your question>"
# answer = qa({"query": question})
# print(answer)

# # Save to DB
