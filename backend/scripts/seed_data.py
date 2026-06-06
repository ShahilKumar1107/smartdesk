# seed_data.py — Populates the database with fake data for testing

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.models.models import Order, User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SAMPLE_ORDERS = [
    {
        "order_id": "ORD-001",
        "customer_email": "alice@example.com",
        "product_name": "Wireless Noise-Cancelling Headphones",
        "quantity": 1,
        "total_price": 299.99,
        "status": "delivered",
        "shipping_address": "123 Main St, New York, NY 10001"
    },
    {
        "order_id": "ORD-002",
        "customer_email": "bob@example.com",
        "product_name": "Mechanical Keyboard",
        "quantity": 1,
        "total_price": 149.99,
        "status": "shipped",
        "shipping_address": "456 Oak Ave, San Francisco, CA 94102"
    },
    {
        "order_id": "ORD-003",
        "customer_email": "carol@example.com",
        "product_name": "USB-C Hub 7-in-1",
        "quantity": 2,
        "total_price": 89.98,
        "status": "processing",
        "shipping_address": "789 Pine Rd, Austin, TX 78701"
    },
    {
        "order_id": "ORD-004",
        "customer_email": "alice@example.com",
        "product_name": "Laptop Stand Adjustable",
        "quantity": 1,
        "total_price": 49.99,
        "status": "shipped",
        "shipping_address": "123 Main St, New York, NY 10001"
    },
    {
        "order_id": "ORD-005",
        "customer_email": "david@example.com",
        "product_name": "Webcam 4K Pro",
        "quantity": 1,
        "total_price": 199.99,
        "status": "cancelled",
        "shipping_address": "321 Elm St, Chicago, IL 60601"
    },
    {
        "order_id": "ORD-006",
        "customer_email": "bob@example.com",
        "product_name": "Desk Lamp LED Smart",
        "quantity": 3,
        "total_price": 119.97,
        "status": "delivered",
        "shipping_address": "456 Oak Ave, San Francisco, CA 94102"
    },
]

SAMPLE_USERS = [
    {
        "email": "alice@example.com",
        "username": "alice",
        "password": "password123"
    },
    {
        "email": "bob@example.com",
        "username": "bob",
        "password": "password123"
    },
]


async def seed():
    engine = create_async_engine(settings.database_url, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)

    async with AsyncSessionLocal() as session:
        print("Seeding users...")
        for user_data in SAMPLE_USERS:
            plain_password = str(user_data["password"])[:72]
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=pwd_context.hash(plain_password)
            )
            session.add(user)

        print("Seeding orders...")
        for order_data in SAMPLE_ORDERS:
            order = Order(**order_data)
            session.add(order)

        await session.commit()
        print("✅ Database seeded successfully!")
        print(f"   - {len(SAMPLE_USERS)} users created")
        print(f"   - {len(SAMPLE_ORDERS)} orders created")

    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(seed())
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")