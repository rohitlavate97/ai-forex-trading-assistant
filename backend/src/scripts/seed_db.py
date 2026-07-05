import asyncio
import sys
import os
from sqlalchemy import select

# Add parent directory to sys.path so we can import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.database import async_session_maker, async_engine
from src.modules.auth.models import User, UserRole
from src.modules.auth.security import get_password_hash
from src.modules.economic_calendar.models import EconomicEvent, EventImportance
from datetime import datetime, timedelta


async def seed_data() -> None:
    """Seed default administrative accounts, trader accounts, and economic events."""
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
                
            # 3. Seed Economic Events
            events_to_seed = [
                {
                    "event_name": "Fed Interest Rate Decision",
                    "country": "United States",
                    "currency": "USD",
                    "importance": EventImportance.HIGH,
                    "event_time": datetime(2026, 7, 8, 18, 0, 0),
                    "forecast": "5.25%",
                    "previous": "5.25%",
                },
                {
                    "event_name": "ECB Monetary Policy Statement",
                    "country": "Eurozone",
                    "currency": "EUR",
                    "importance": EventImportance.HIGH,
                    "event_time": datetime(2026, 7, 9, 12, 15, 0),
                    "forecast": "4.00%",
                    "previous": "4.25%",
                },
                {
                    "event_name": "US CPI Inflation MoM",
                    "country": "United States",
                    "currency": "USD",
                    "importance": EventImportance.HIGH,
                    "event_time": datetime(2026, 7, 4, 12, 30, 0),
                    "actual": "0.2%",
                    "forecast": "0.2%",
                    "previous": "0.1%",
                },
                {
                    "event_name": "UK GDP MoM",
                    "country": "United Kingdom",
                    "currency": "GBP",
                    "importance": EventImportance.MEDIUM,
                    "event_time": datetime(2026, 7, 2, 7, 0, 0),
                    "actual": "-0.1%",
                    "forecast": "0.1%",
                    "previous": "0.2%",
                },
                {
                    "event_name": "Australia Unemployment Rate",
                    "country": "Australia",
                    "currency": "AUD",
                    "importance": EventImportance.HIGH,
                    "event_time": datetime(2026, 7, 16, 1, 30, 0),
                    "forecast": "4.0%",
                    "previous": "3.9%",
                }
            ]
            
            for ev in events_to_seed:
                result_ev = await session.execute(
                    select(EconomicEvent).where(EconomicEvent.event_name == ev["event_name"])
                )
                existing_ev = result_ev.scalars().first()
                if not existing_ev:
                    print(f"Creating economic event: {ev['event_name']}")
                    session.add(EconomicEvent(**ev))
                else:
                    print(f"Economic event already exists: {ev['event_name']}. Skipping...")
                    
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
