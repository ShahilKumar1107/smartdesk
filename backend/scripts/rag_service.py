# rag_service.py — Retrieves relevant FAQ chunks from ChromaDB

import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from app.core.config import settings

CHROMA_DB_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "chroma_db"
)

def get_vectorstore() -> Chroma:
    """Loads the ChromaDB vector store from disk."""
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=settings.google_api_key
    )
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings,
        collection_name="smartdesk_faq"
    )
    return vectorstore

def search_knowledge_base(query: str, k: int = 3) -> str:
    """Searches the knowledge base for chunks relevant to the query."""
    try:
        vectorstore = get_vectorstore()
        results = vectorstore.similarity_search(query, k=k)

        if not results:
            return "No relevant information found in the knowledge base."

        formatted_results = []
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("source", "Unknown")
            formatted_results.append(
                f"[Result {i} from {source}]\n{doc.page_content}"
            )

        return "\n\n".join(formatted_results)

    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"