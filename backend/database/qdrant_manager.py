from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from dotenv import load_dotenv
import os

from backend.models.embedding import EMBEDDING_MODEL

load_dotenv()

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



class QdrantManager:
    def __init__(self, embedding_model):
        # Qdrant Cloud 設定
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.embedding_model = embedding_model
        self.collection_name = "documents"
        
        # 確保集合存在
        self._ensure_collection()
    
    def _ensure_collection(self):
        """確保集合存在，如果不存在就建立"""
        collections = self.client.get_collections().collections
        exists = any(col.name == self.collection_name for col in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1024,  # BGE-M3 的向量維度
                    distance=Distance.COSINE
                )
            )
    
    def split_and_add_text(self, docs):
        texts = text_splitter.split_text(docs)
        return QdrantVectorStore.from_documents(
            documents=[Document(page_content=t) for t in texts],
            embedding=self.embedding_model,
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            collection_name=self.collection_name,
            prefer_grpc=True
        )
    
    def get_vectordb(self):
        return QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embedding_model,
        )
    
    def clear_collection(self):
        self.client.delete_collection(self.collection_name)
        self._ensure_collection()

    def split_and_add_summary(self, summary_md, folder_name):
        texts = text_splitter.split_text(summary_md)
        return QdrantVectorStore.from_documents(
            documents=[Document(page_content=t, metadata={"folder_name": folder_name}) for t in texts],
            embedding=self.embedding_model,
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            collection_name=self.collection_name,
            prefer_grpc=True
        )
    
    # Delete summary from vector database(metadata = folder_name)
    def delete_summary(self, folder_name):
        metadata_filter = {
            "must": [
                {
                    "key": "metadata.folder_name",
                    "match": {
                        "value": folder_name
                    }
                }
            ]
        }

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=metadata_filter
            )
        )


if __name__ == "__main__":

    qdrant_manager = QdrantManager(EMBEDDING_MODEL)
    # qdrant_manager.clear_collection()
    
    # # Add summary to vector database(metadata = folder_name)
    # qdrant_manager.split_and_add_summary(
    #     "test",
    #     "20241130_041824"
    # )

    # Delete summary from vector database(metadata = folder_name)
    qdrant_manager.delete_summary("20241130_041824")
