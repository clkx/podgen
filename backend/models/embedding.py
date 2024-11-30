from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL = HuggingFaceEmbeddings(
    model_name='BAAI/bge-m3',
    model_kwargs={'device': 'cuda'},
    encode_kwargs={'normalize_embeddings': False}
)