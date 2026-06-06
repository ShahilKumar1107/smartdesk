# escalation_tool.py — Tool that creates a support ticket
# The agent calls this when it cannot resolve the customer's issue

from langchain.tools import tool
from sqlalchemy import create_engine, text
from datetime import datetime
from app.core.config import settings

@tool
def escalation_tool(issue_description: str) -> str:
    """
    Create a support ticket to escalate an issue to a human agent.
    Use this tool when:
    - The customer's issue cannot be resolved with FAQ or order lookup
    - The customer is frustrated or explicitly asks for human support
    - The issue requires manual intervention
    Input should be a clear description of the customer's issue.
    """
    print(f"🎫 Escalation Tool called with issue: {issue_description}")

    try:
        engine = create_engine(settings.sync_database_url)

        # Generate a unique ticket ID using timestamp
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
                    "email": "guest@smartdesk.com",  # Will be updated with real user in Phase 7
                    "description": issue_description,
                    "status": "open",
                    "priority": "medium"
                }
            )
            conn.commit()

        return f"""
Support ticket created successfully!
- Ticket ID: {ticket_id}
- Status: Open
- Priority: Medium
- A human agent will contact you within 2-4 business hours.
- Please save your ticket ID for reference: {ticket_id}
"""

    except Exception as e:
        return f"Error creating support ticket: {str(e)}"