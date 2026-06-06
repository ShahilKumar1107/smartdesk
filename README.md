# SmartDesk 🤖

**An Agentic AI Customer Support Platform**

SmartDesk is a full-stack web application where customers type support queries in a chat UI, and a LangChain ReAct AI agent automatically resolves them using intelligent tools.

## Features
- 🧠 **AI Agent** — LangChain ReAct agent with 3 specialized tools
- 📚 **RAG Pipeline** — FAQ search using ChromaDB + OpenAI embeddings
- 🛒 **Order Lookup** — Real-time order status from PostgreSQL
- 🎫 **Auto Escalation** — Creates support tickets when AI can't help
- 💬 **Streaming Chat** — Word-by-word responses like ChatGPT
- 🔐 **JWT Auth** — Secure user authentication

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, LangChain |
| AI | OpenAI API, ChromaDB |
| Database | PostgreSQL, SQLAlchemy |
| Frontend | React.js (Vite), Tailwind CSS |
| Auth | JWT |

## Project Structure
```
SmartDesk/
├── backend/     # FastAPI + LangChain backend
├── frontend/    # React.js frontend
└── README.md
```

## Getting Started
See the setup instructions in each subfolder's README.
