# order_tool.py — Tool that looks up order information from PostgreSQL
# The agent calls this when customers ask about their orders

from langchain.tools import tool
from sqlalchemy import create_engine, text
from app.core.config import settings

@tool
def order_lookup_tool(order_id: str) -> str:
    """
    Look up order information from the database using an order ID.
    Use this tool when a customer asks about their order status,
    shipping, or any order-specific information.
    Input should be the order ID (e.g. 'ORD-001', 'ORD-002').
    """
    print(f"📦 Order Lookup Tool called with order_id: {order_id}")

    try:
        # Use synchronous engine for tool (simpler than async here)
        engine = create_engine(settings.sync_database_url)

        with engine.connect() as conn:
            # Clean the order_id — remove extra spaces and uppercase it
            clean_order_id = order_id.strip().upper()

            result = conn.execute(
                text("SELECT * FROM orders WHERE UPPER(order_id) = :order_id"),
                {"order_id": clean_order_id}
            )
            order = result.fetchone()

            if not order:
                return f"No order found with ID '{order_id}'. Please check the order ID and try again."

            # Format the order information nicely
            return f"""
Order Found:
- Order ID: {order.order_id}
- Product: {order.product_name}
- Quantity: {order.quantity}
- Total Price: ${order.total_price:.2f}
- Status: {order.status.upper()}
- Shipping Address: {order.shipping_address}
- Order Date: {order.created_at}
"""

    except Exception as e:
        return f"Error looking up order: {str(e)}"