import asyncio
from backend.app.core.database import SessionLocal, engine
from backend.app.models.user import User, UserRole
from backend.app.models.product import Category, Product
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def verify_db():
    async with SessionLocal() as session:
        # 1. Create a category
        category = Category(name="Electronics", description="Gadgets and devices")
        session.add(category)
        await session.commit()
        await session.refresh(category)
        category_id = category.id
        print(f"Created category: {category.name} (ID: {category_id})")

        # 2. Create a product
        product = Product(
            name="Smartphone",
            sku="PHONE-001",
            price=500.0,
            stock_quantity=10,
            category_id=category_id
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)
        product_id = product.id
        print(f"Created product: {product.name} (SKU: {product.sku}, ID: {product_id})")

        # 3. Create a user
        user = User(
            username="admin",
            email="admin@example.com",
            hashed_password="fakehash",
            full_name="Admin User",
            role=UserRole.ADMIN
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(f"Created user: {user.username}")

        # 4. Verify relations
        stmt = select(Product).options(selectinload(Product.category)).where(Product.id == product_id)
        result = await session.execute(stmt)
        p = result.scalar_one()
        print(f"Product {p.name} belongs to category: {p.category.name}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify_db())
