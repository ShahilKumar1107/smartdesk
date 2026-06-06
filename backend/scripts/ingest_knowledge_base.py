# ingest_knowledge_base.py — Reads FAQ files and stores them in ChromaDB
# Using Google Gemini embeddings (free)

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from app.core.config import settings

KNOWLEDGE_BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "knowledge_base"
)

CHROMA_DB_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "chroma_db"
)

def ingest():
    print("🚀 Starting knowledge base ingestion...")

    # ── Step 1: Load all text files ──────────────────────────
    documents = []
    txt_files = [f for f in os.listdir(KNOWLEDGE_BASE_DIR) if f.endswith(".txt")]

    if not txt_files:
        print("❌ No .txt files found in knowledge_base folder!")
        return

    for filename in txt_files:
        filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
        print(f"   Loading: {filename}")
        loader = TextLoader(filepath, encoding="utf-8")
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = filename
        documents.extend(docs)

    print(f"✅ Loaded {len(documents)} documents")

    # ── Step 2: Split into chunks ─────────────────────────────
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "Q:", "A:"]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Split into {len(chunks)} chunks")

    # ── Step 3: Create embeddings using Google Gemini ─────────
    print("🔄 Creating embeddings using Google Gemini...")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=settings.google_api_key
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR,
        collection_name="smartdesk_faq"
    )

    print(f"✅ Stored {len(chunks)} chunks in ChromaDB")
    print(f"✅ Knowledge base ingestion complete!")

if __name__ == "__main__":
    try:
        ingest()
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")