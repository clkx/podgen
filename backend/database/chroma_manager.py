from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from uuid import uuid4
from langchain_core.documents import Document
from typing import List, Optional, Dict, Any
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

class ChromaDBManager:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(current_dir, 'chromadb')
        
        # 確保資料庫目錄存在
        os.makedirs(self.db_path, exist_ok=True)
        
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        self.vector_store = Chroma(
            collection_name="references_collection",
            embedding_function=self.embeddings,
            persist_directory=self.db_path
        )
    
    def create_documents(self, documents: List[Document]) -> List[str]:
        """新增文件到向量資料庫
        
        Args:
            documents: 要新增的文件列表
            
        Returns:
            新增文件的 UUID 列表
        """
        uuids = [str(uuid4()) for _ in range(len(documents))]
        self.vector_store.add_documents(documents=documents, ids=uuids)
        return uuids
    
    def search_documents(self, 
                      query: str, 
                      k: int = 4,
                      filter: Optional[Dict[str, Any]] = None) -> List[Document]:
        """搜尋相似文件
        
        Args:
            query: 搜尋查詢字串
            k: 要返回的文件數量
            filter: 過濾條件
            
        Returns:
            相似文件列表
        """
        return self.vector_store.similarity_search(
            query,
            k=k,
            filter=filter
        )
    
    def update_document(self, 
                       document_id: str, 
                       new_document: Document) -> None:
        """更新文件
        
        Args:
            document_id: 要更新的文件 ID
            new_document: 新的文件內容
        """
        self.vector_store.update_document(
            document_id=document_id,
            document=new_document
        )
    
    def delete_documents(self, ids: List[str]) -> None:
        """刪除文件
        
        Args:
            ids: 要刪除的文件 ID 列表
        """
        self.vector_store.delete(ids=ids)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """獲取集合統計資訊
        
        Returns:
            集合的統計資訊
        """
        return self.vector_store._collection.count()
    
    def load_pdf(self, pdf_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """載入 PDF 並儲存到向量資料庫
        
        Args:
            pdf_path: PDF 檔案路徑
            chunk_size: 每個文本塊的大小
            chunk_overlap: 文本塊重疊的大小
            
        Returns:
            儲存的文件 ID 列表
        """
        # 載入 PDF
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        
        # 分割文本
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = text_splitter.split_documents(pages)
        
        # 為每個 chunk 添加來源資訊
        for chunk in chunks:
            chunk.metadata["id"] = id
            
        # 儲存到向量資料庫
        return self.create_documents(chunks)
    
    def delete_pdf(self, id: str) -> None:
        """刪除指定來源的所有文件
        
        Args:
            id: 文件 ID
        """
        # 獲取所有符合來源的文件
        results = self.vector_store.get(
            where={"id": id}
        )
        if results and results['id']:
            # 刪除這些文件
            self.delete_documents(results['id'])
    
    def load_md(self, md_path: str) -> List[str]:
        """載入 Markdown 文件並儲存到向量資料庫
        
        Args:
            md_path: Markdown 檔案路徑
            
        Returns:
            儲存的文件 ID 列表
        """
        # 載入 Markdown
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 分割文本
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.create_documents([content])
        
        # 為每個 chunk 添加來源資訊
        for chunk in chunks:
            chunk.metadata["id"] = id
            
        # 儲存到向量資料庫
        return self.create_documents(chunks)
    
    def delete_md(self, id: str) -> None:
        """刪除指定來源的所有文件
        
        Args:
            md_path: Markdown 檔案路徑
        """
        # 獲取所有符合來源的文件
        results = self.vector_store.get(
            where={"id": id}
        )
        if results and results['id']:
            # 刪除這些文件
            self.delete_documents(results['id'])

    def reset_collection(self) -> None:
        """重置集合"""
        self.vector_store.delete_collection()
        self.vector_store = Chroma(
            collection_name="references_collection",
            embedding_function=self.embeddings,
            persist_directory=self.db_path
        )


if __name__ == "__main__":
    db_manager = ChromaDBManager()

    # 測試建立文件功能
    print("測試建立文件...")
    test_docs = [
        Document(
            page_content="這是一個測試文件的內容",
            metadata={"source": "test_source", "type": "test"}
        ),
        Document(
            page_content="這是另一個測試文件",
            metadata={"source": "test_source", "type": "test"} 
        )
    ]
    doc_ids = db_manager.create_documents(test_docs)
    print(f"成功建立 {len(doc_ids)} 個文件")



    # 測試搜尋功能
    print("\n測試搜尋文件...")
    search_results = db_manager.search_documents(
        query="測試文件",
        k=2,
        filter={"type": "test"}
    )
    print(f"搜尋到 {len(search_results)} 個相關文件")
    for i, doc in enumerate(search_results):
        print(f"文件 {i+1}: {doc.page_content}")




    # 測試更新功能
    print("\n測試更新文件...")
    updated_doc = Document(
        page_content="這是更新後的測試內容",
        metadata={"source": "test_source", "type": "test"}
    )
    db_manager.update_document(doc_ids[0], updated_doc)
    print("文件更新完成")



    # 測試刪除功能
    print("\n測試刪除文件...")
    db_manager.delete_documents(doc_ids)
    print(f"已刪除 {len(doc_ids)} 個文件")

    db_manager.load_pdf("C:\\Users\\k123k\\Desktop\\podgen\\backend\\stores\\references\\20241125_121830\\20241125_121830_original.pdf")
    db_manager.delete_pdf("C:\\Users\\k123k\\Desktop\\podgen\\backend\\stores\\references\\20241125_121830\\20241125_121830_original.pdf")

    # 測試統計功能
    print("\n測試獲取統計資訊...")
    collection_stats = db_manager.get_collection_stats()
    print(f"集合統計資訊: {collection_stats}")