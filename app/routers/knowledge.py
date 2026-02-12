from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import KnowledgeItem
from app.schemas import KnowledgeCreate
from app.services.logging_service import write_log

router = APIRouter(prefix='/knowledge', tags=['knowledge'])


@router.post('/items')
def create_knowledge_item(payload: KnowledgeCreate, db: Session = Depends(get_db)):
    item = KnowledgeItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    write_log(db, action='knowledge.create', details=f'Knowledge item {item.id} created')
    return item


@router.get('/items')
def list_knowledge_items(db: Session = Depends(get_db), limit: int = 50):
    return db.query(KnowledgeItem).order_by(KnowledgeItem.created_at.desc()).limit(limit).all()
