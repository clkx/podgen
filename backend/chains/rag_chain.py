from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.document_compressors import FlashrankRerank
from langchain.retrievers import ContextualCompressionRetriever

from backend.models.llm import LLM  
from backend.database.qdrant_manager import QdrantManager
from backend.models.embedding import EMBEDDING_MODEL

# 初始化 Qdrant manager
qdrant_manager = QdrantManager(EMBEDDING_MODEL)

vectordb = qdrant_manager.get_vectordb()

# 使用 vectordb 創建檢索器
retriever = vectordb.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 10}
)

prompt = PromptTemplate.from_template("""
<system instruction>
{context}
Question: {question}
Helpful Answer:""")

RERANK_MODEL = 'ms-marco-MultiBERT-L-12'

compressor = FlashrankRerank(model=RERANK_MODEL, top_n=5)  # K2, Top5 Answers
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, 
    base_retriever=retriever
)

rag_chain = (
    {"context": compression_retriever, "question": RunnablePassthrough()} 
    | prompt 
    | LLM 
    | StrOutputParser()
)


if __name__ == "__main__":

    qdrant_manager.clear_collection()
    text = open(r"C:\Users\k123k\Desktop\podgen\backend\test.txt", "r", encoding="utf-8").read()
    qdrant_manager.split_and_add_text(text)
    
    question = "什麼是COWOS"
    search_result = compression_retriever.invoke(question)
    print(search_result)