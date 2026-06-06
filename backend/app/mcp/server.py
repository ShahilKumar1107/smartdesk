# server.py — MCP Server that exposes SmartDesk tools
# This makes our tools available via the Model Context Protocol
# Any MCP-compatible AI client can now use these tools

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.rag_service import search_knowledge_base
from sqlalchemy import create_engine, text
from app.core.config import settings
from datetime import datetime

# Create the MCP server instance
server = Server("smartdesk")

# ─── DEFINE TOOLS ────────────────────────────────────────────
# Each tool has a name, description, and input schema
# The description is critical — the AI uses it to decide when to call the tool

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Returns the list of available tools to the AI client."""
    return [
        Tool(
            name="search_faq",
            description="""Search the SmartDesk FAQ knowledge base for answers.
            Use this for questions about policies, shipping, returns, products,
            account issues, or any general information about SmartDesk.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The customer's question to search for"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="lookup_order",
            description="""Look up order information from the database.
            Use this when a customer asks about their order status,
            shipping details, or any order-specific information.
            Requires an order ID like 'ORD-001'.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order ID to look up (e.g. 'ORD-001')"
                    }
                },
                "required": ["order_id"]
            }
        ),
        Tool(
            name="create_ticket",
            description="""Create a support ticket to escalate an issue to a human agent.
            Use this when the customer's issue cannot be resolved with FAQ or order lookup,
            or when the customer explicitly asks for human support.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_description": {
                        "type": "string",
                        "description": "Clear description of the customer's issue"
                    },
                    "customer_email": {
                        "type": "string",
                        "description": "Customer's email address"
                    }
                },
                "required": ["issue_description", "customer_email"]
            }
        )
    ]

# ─── HANDLE TOOL CALLS ───────────────────────────────────────

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Executes the requested tool and returns the result."""

    if name == "search_faq":
        query = arguments.get("query", "")
        result = search_knowledge_base(query)
        return [TextContent(type="text", text=result)]

    elif name == "lookup_order":
        order_id = arguments.get("order_id", "").strip().upper()
        try:
            engine = create_engine(settings.sync_database_url)
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT * FROM orders WHERE UPPER(order_id) = :order_id"),
                    {"order_id": order_id}
                )
                order = result.fetchone()
                if not order:
                    return [TextContent(
                        type="text",
                        text=f"No order found with ID '{order_id}'."
                    )]
                return [TextContent(
                    type="text",
                    text=f"""Order Found:
- Order ID: {order.order_id}
- Product: {order.product_name}
- Quantity: {order.quantity}
- Total: ${order.total_price:.2f}
- Status: {order.status.upper()}
- Address: {order.shipping_address}"""
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "create_ticket":
        issue = arguments.get("issue_description", "")
        email = arguments.get("customer_email", "guest@smartdesk.com")
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
                        "email": email,
                        "description": issue,
                        "status": "open",
                        "priority": "medium"
                    }
                )
                conn.commit()
            return [TextContent(
                type="text",
                text=f"Support ticket created! Ticket ID: {ticket_id}. A human agent will contact you within 2-4 business hours."
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error creating ticket: {str(e)}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Runs the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())