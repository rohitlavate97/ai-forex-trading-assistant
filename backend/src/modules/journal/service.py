from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from typing import List, Optional

from src.modules.journal.models import JournalEntry
from src.modules.journal.schemas import JournalEntryCreate, JournalEntryUpdate

class JournalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_entry(self, user_id: str, entry_in: JournalEntryCreate) -> JournalEntry:
        db_entry = JournalEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            currency_pair=entry_in.currency_pair,
            direction=entry_in.direction,
            entry_price=entry_in.entry_price,
            exit_price=entry_in.exit_price,
            profit_loss=entry_in.profit_loss,
            notes=entry_in.notes,
            tags=entry_in.tags if entry_in.tags else []
        )
        self.db.add(db_entry)
        await self.db.commit()
        await self.db.refresh(db_entry)
        return db_entry

    async def get_entries(self, user_id: str) -> List[JournalEntry]:
        query = select(JournalEntry).where(JournalEntry.user_id == user_id).order_by(JournalEntry.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_entry(self, user_id: str, entry_id: str) -> Optional[JournalEntry]:
        query = select(JournalEntry).where(
            JournalEntry.id == entry_id, 
            JournalEntry.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_entry(self, user_id: str, entry_id: str, entry_update: JournalEntryUpdate) -> Optional[JournalEntry]:
        db_entry = await self.get_entry(user_id, entry_id)
        if not db_entry:
            return None

        update_data = entry_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_entry, key, value)

        await self.db.commit()
        await self.db.refresh(db_entry)
        return db_entry

    async def delete_entry(self, user_id: str, entry_id: str) -> bool:
        db_entry = await self.get_entry(user_id, entry_id)
        if not db_entry:
            return False

        await self.db.delete(db_entry)
        await self.db.commit()
        return True
