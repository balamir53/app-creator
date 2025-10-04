"""
Items router for CRUD operations
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.item import Item, ItemCreate, ItemUpdate
from app.services.item_service import ItemService

router = APIRouter()


@router.get("/items", response_model=List[Item])
async def get_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all items"""
    items = ItemService.get_items(db, skip=skip, limit=limit)
    return items


@router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific item by ID"""
    item = ItemService.get_item(db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/items", response_model=Item)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item"""
    return ItemService.create_item(db=db, item=item)


@router.put("/items/{item_id}", response_model=Item)
async def update_item(
    item_id: int,
    item: ItemUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing item"""
    updated_item = ItemService.update_item(db=db, item_id=item_id, item=item)
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item


@router.delete("/items/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item"""
    success = ItemService.delete_item(db=db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}