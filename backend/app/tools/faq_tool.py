# faq_tool.py — Tool that searches the FAQ knowledge base
# The agent calls this when it needs to answer general questions

from langchain.tools import tool
from app.services.rag_service import search_knowledge_base

@tool
def faq_tool(query: str) -> str:
    """
    Search the FAQ knowledge base for answers to customer questions.
    Use this tool when customers ask about policies, shipping, returns,
    products, account issues, or any general information.
    Input should be the customer's question as a string.
    """
    print(f"🔍 FAQ Tool called with query: {query}")
    result = search_knowledge_base(query)
    return result