"""
Service layer for Item operations
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.models import Item
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    @staticmethod
    def get_item(db: Session, item_id: int) -> Optional[Item]:
        """Get a single item by ID"""
        return db.query(Item).filter(Item.id == item_id).first()

    @staticmethod
    def get_items(db: Session, skip: int = 0, limit: int = 100) -> List[Item]:
        """Get multiple items with pagination"""
        return db.query(Item).offset(skip).limit(limit).all()

    @staticmethod
    def create_item(db: Session, item: ItemCreate) -> Item:
        """Create a new item"""
        db_item = Item(**item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    @staticmethod
    def update_item(db: Session, item_id: int, item: ItemUpdate) -> Optional[Item]:
        """Update an existing item"""
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if db_item:
            update_data = item.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_item, field, value)
            db.commit()
            db.refresh(db_item)
        return db_item

    @staticmethod
    def delete_item(db: Session, item_id: int) -> bool:
        """Delete an item"""
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if db_item:
            db.delete(db_item)
            db.commit()
            return True
        return False