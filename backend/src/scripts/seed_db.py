import asyncio
import sys
import os
from sqlalchemy import select

# Add parent directory to sys.path so we can import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.database import async_session_maker, async_engine
from src.modules.auth.models import User, UserRole
from src.modules.auth.security import get_password_hash


async def seed_data() -> None:
    """Seed default administrative and trader accounts into the database."""
    print("Database seeding started...")
    
    async with async_session_maker() as session:
        try:
            # 1. Seed Admin User
            admin_username = "admin"
            admin_email = "admin@forex.com"
            result_admin = await session.execute(
                select(User).where(User.username == admin_username)
            )
            existing_admin = result_admin.scalars().first()
            
            if not existing_admin:
                print(f"Creating default admin account: {admin_username} ({admin_email})")
                admin_user = User(
                    username=admin_username,
                    email=admin_email,
                    hashed_password=get_password_hash("AdminPassword123"),
                    role=UserRole.ADMIN,
                )
                session.add(admin_user)
            else:
                print("Admin account already exists. Skipping...")
                
            # 2. Seed Trader User
            trader_username = "trader"
            trader_email = "trader@forex.com"
            result_trader = await session.execute(
                select(User).where(User.username == trader_username)
            )
            existing_trader = result_trader.scalars().first()
            
            if not existing_trader:
                print(f"Creating default trader account: {trader_username} ({trader_email})")
                trader_user = User(
                    username=trader_username,
                    email=trader_email,
                    hashed_password=get_password_hash("TraderPassword123"),
                    role=UserRole.TRADER,
                )
                session.add(trader_user)
            else:
                print("Trader account already exists. Skipping...")
                
            await session.commit()
            print("Database seeding completed successfully.")
            
        except Exception as e:
            await session.rollback()
            print(f"Error seeding database: {e}")
            raise
        finally:
            await session.close()
            
    # Dispose engine connections
    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())
