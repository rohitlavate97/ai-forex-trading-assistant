from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any

from src.modules.auth.dependencies import get_current_user
from src.core.database import get_db
from src.modules.journal.schemas import JournalEntryCreate, JournalEntryUpdate, JournalEntryResponse
from src.modules.journal.service import JournalService

router = APIRouter(prefix="/journal", tags=["Trading Journal"])


@router.post("/", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    entry: JournalEntryCreate,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = JournalService(db)
    return await service.create_entry(current_user["id"], entry)


@router.get("/", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = JournalService(db)
    return await service.get_entries(current_user["id"])


@router.get("/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: str,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = JournalService(db)
    entry = await service.get_entry(current_user["id"], entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return entry


@router.patch("/{entry_id}", response_model=JournalEntryResponse)
async def update_journal_entry(
    entry_id: str,
    entry_update: JournalEntryUpdate,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = JournalService(db)
    entry = await service.update_entry(current_user["id"], entry_id, entry_update)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journal_entry(
    entry_id: str,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = JournalService(db)
    success = await service.delete_entry(current_user["id"], entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Journal entry not found")
