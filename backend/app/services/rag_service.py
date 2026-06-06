import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings

KNOWLEDGE_BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "knowledge_base"
)

def search_knowledge_base(query: str, k: int = 3) -> str:
    """Simple keyword search for production deployment."""
    try:
        results = []
        query_lower = query.lower()
        
        for filename in os.listdir(KNOWLEDGE_BASE_DIR):
            if filename.endswith(".txt"):
                filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                paragraphs = content.split("\n\n")
                for para in paragraphs:
                    if any(word in para.lower() for word in query_lower.split()):
                        results.append(f"[From {filename}]\n{para.strip()}")
                        if len(results) >= k:
                            break
            if len(results) >= k:
                break

        if not results:
            return "No relevant information found in the knowledge base."
        
        return "\n\n".join(results)

    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"