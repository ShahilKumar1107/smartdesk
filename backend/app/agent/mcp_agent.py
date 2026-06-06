# mcp_agent.py — Agent that uses MCP protocol for tool calls
# This shows how MCP makes tool integration cleaner and more standardized

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
from app.core.config import settings
from app.services.rag_service import search_knowledge_base
from sqlalchemy import create_engine, text
from datetime import datetime

# ─── MCP-STYLE TOOLS ─────────────────────────────────────────
# These tools follow MCP naming and description conventions
# Making them easy to swap with actual MCP server tools later

@tool
def search_faq(query: str) -> str:
    """Search the SmartDesk FAQ knowledge base for answers.
    Use this for questions about policies, shipping, returns, products,
    account issues, or any general information about SmartDesk."""
    print(f"🔍 MCP FAQ Tool: {query}")
    return search_knowledge_base(query)

@tool
def lookup_order(order_id: str) -> str:
    """Look up order information from the database.
    Use this when a customer asks about their order status,
    shipping details, or any order-specific information.
    Requires an order ID like 'ORD-001'."""
    print(f"📦 MCP Order Tool: {order_id}")
    try:
        engine = create_engine(settings.sync_database_url)
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM orders WHERE UPPER(order_id) = :order_id"),
                {"order_id": order_id.strip().upper()}
            )
            order = result.fetchone()
            if not order:
                return f"No order found with ID '{order_id}'."
            return f"""Order Found:
- Order ID: {order.order_id}
- Product: {order.product_name}
- Status: {order.status.upper()}
- Address: {order.shipping_address}"""
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def create_ticket(issue_description: str, customer_email: str = "guest@smartdesk.com") -> str:
    """Create a support ticket to escalate an issue to a human agent.
    Use this when the customer's issue cannot be resolved with FAQ or order lookup,
    or when the customer explicitly asks for human support."""
    print(f"🎫 MCP Escalation Tool: {issue_description}")
    try:
        engine = create_engine(settings.sync_database_url)
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO support_tickets
                    (ticket_id, customer_email, issue_description, status, priority)
                    VALUES (:ticket_id, :email, :description, :status, :priority)
                """),
                {
                    "ticket_id": ticket_id,
                    "email": customer_email,
                    "description": issue_description,
                    "status": "open",
                    "priority": "medium"
                }
            )
            conn.commit()
        return f"Ticket {ticket_id} created! A human agent will contact you within 2-4 hours."
    except Exception as e:
        return f"Error: {str(e)}"

# MCP-style tools list
MCP_TOOLS = [search_faq, lookup_order, create_ticket]

SYSTEM_PROMPT = """You are a helpful customer support agent for SmartDesk.

Guidelines:
- Always be polite and professional
- Use lookup_order for order-related questions
- Use search_faq for general questions
- Use create_ticket when you cannot resolve the issue
- Always provide clear, helpful responses"""

def create_mcp_agent():
    """Creates agent using MCP-style tools."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.google_api_key,
        temperature=0.3,
    )
    agent = create_react_agent(
        model=llm,
        tools=MCP_TOOLS,
        prompt=SYSTEM_PROMPT
    )
    return agent

mcp_agent_executor = create_mcp_agent()

def run_mcp_agent(user_message: str) -> str:
    """Runs the MCP agent."""
    try:
        result = mcp_agent_executor.invoke({
            "messages": [{"role": "user", "content": user_message}]
        })
        messages = result.get("messages", [])
        if messages:
            content = messages[-1].content
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        return item["text"]
            return str(content)
        return "I couldn't process your request."
    except Exception as e:
        return f"Error: {str(e)}"