from langchain_core.documents import Document
import arxiv
from langchain_core.messages import SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import WikipediaLoader
from langchain.retrievers.document_compressors import FlashrankRerank
from langchain.retrievers import ContextualCompressionRetriever

from backend.states import InterviewState
from backend.schema import SearchQuery
from backend.models.llm import LLM
from backend.database.qdrant_manager import QdrantManager
from backend.models.embedding import EMBEDDING_MODEL

# Search query writing
search_instructions = SystemMessage(content=f"""You will be given a conversation between an analyst and an expert. 

Your goal is to generate a well-structured query for use in retrieval and / or web-search related to the conversation.
        
First, analyze the full conversation.

Pay particular attention to the final question posed by the analyst.

Convert this final question into a well-structured web search query""")



def search_arxiv_node(state: InterviewState):
    """ Retrieve docs from arxiv """

    # Search query
    structured_llm = LLM.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([search_instructions]+state['messages'])
    
    try:
        # Search arXiv
        search = arxiv.Search(
            query=search_query.search_query,
            max_results=10,
            sort_by=arxiv.SortCriterion.Relevance
        )

        # Retrieve results
        search_docs = []
        for result in search.results():
            doc = Document(
                page_content=f"{result.title}\n\n{result.summary}",
                metadata={
                    "title": result.title,
                    "authors": ", ".join(author.name for author in result.authors),
                    "published": result.published.strftime("%Y-%m-%d"),
                    "url": result.entry_id,
                }
            )
            search_docs.append(doc)

        # Format
        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document title="{doc.metadata["title"]}" authors="{doc.metadata["authors"]}" published="{doc.metadata["published"]}" url="{doc.metadata["url"]}"/>\n{doc.page_content}\n</Document>'
                for doc in search_docs
            ]
        )

    except arxiv.UnexpectedEmptyPageError:
        print(f"arXiv 搜尋 '{search_query.search_query}' 沒有找到結果")
        formatted_search_docs = ""
        
    except Exception as e:
        print(f"arXiv 搜尋時發生錯誤: {str(e)}")
        formatted_search_docs = ""

    return {"context": [formatted_search_docs]}



def search_web_node(state: InterviewState):
    """ Retrieve docs from web search """

    # Search query
    structured_llm = LLM.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([search_instructions]+state['messages'])
    
    # Search
    tavily_search = TavilySearchResults(max_results=5)
    search_docs = tavily_search.invoke(search_query.search_query)

    # Debug: Print the type and content of search_docs
    print(f"Type of search_docs: {type(search_docs)}")
    print(f"Content of search_docs: {search_docs}")

    # Format
    try:
        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
                for doc in search_docs
            ]
        )
    except TypeError as e:
        print(f"Error in formatting search_docs: {e}")
        # Fallback: treat search_docs as a single string if it's not iterable
        formatted_search_docs = f"<Document>\n{search_docs}\n</Document>"

    return {"context": [formatted_search_docs]} 



def search_wikipedia_node(state: InterviewState):
    """ Retrieve docs from wikipedia """

    # Search query
    structured_llm = LLM.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([search_instructions]+state['messages'])
    
    # Search
    search_docs = WikipediaLoader(query=search_query.search_query, 
                                  load_max_docs=2).load()

     # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}


def search_db_node(state: InterviewState):
    """ Retrieve docs from vector database """

    # Search query
    structured_llm = LLM.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([search_instructions]+state['messages'])

    # Running search
    qdrant_manager = QdrantManager(EMBEDDING_MODEL)
    vectordb = qdrant_manager.get_vectordb()
    # search_docs = vectordb.similarity_search(search_query.search_query, k=10)

    # Create retriever
    retriever = vectordb.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 100}
    )


    RERANK_MODEL = 'ms-marco-MultiBERT-L-12'

    compressor = FlashrankRerank(model=RERANK_MODEL, top_n=5)  # K2, Top5 Answers
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, 
        base_retriever=retriever
    )

    search_docs = compression_retriever.invoke(search_query.search_query)

    # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="user provided knowledge database"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )
    
    return {"context": [formatted_search_docs]}

