# agent.py — The main LangChain agent using modern langgraph approach

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from app.core.config import settings
from app.tools.faq_tool import faq_tool
from app.tools.order_tool import order_lookup_tool
from app.tools.escalation_tool import escalation_tool

# List of tools the agent can use
TOOLS = [faq_tool, order_lookup_tool, escalation_tool]

# System prompt
SYSTEM_PROMPT = """You are a helpful customer support agent for SmartDesk, an online tech products store.

Guidelines:
- Always be polite and professional
- If a customer asks about an order, use the order_lookup_tool
- If a customer asks general questions, use the faq_tool  
- If you cannot resolve an issue after trying the tools, use escalation_tool
- Always provide clear, helpful responses
- If you create a support ticket, include the ticket ID in your response"""

def create_agent():
    """Creates and returns the LangChain ReAct agent."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.google_api_key,
        temperature=0.3,
    )

    agent = create_react_agent(
        model=llm,
        tools=TOOLS,
        prompt=SYSTEM_PROMPT
    )

    return agent

# Create a single shared agent instance
agent_executor = create_agent()

def run_agent(user_message: str) -> str:
    """Runs the agent with a user message and returns the response."""
    try:
        result = agent_executor.invoke({
            "messages": [{"role": "user", "content": user_message}]
        })
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            # Handle both string and list content formats
            content = last_message.content
            if isinstance(content, list):
                # Extract text from list format
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        return item["text"]
            return str(content)
        return "I'm sorry, I couldn't process your request."
    except Exception as e:
        return f"I encountered an error: {str(e)}. Please try again."