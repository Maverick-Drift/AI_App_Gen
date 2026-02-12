from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SearchRequest
from app.services.agent import generate_content, internet_search

router = APIRouter(prefix='/agent', tags=['agent'])


@router.post('/search')
def search_web(payload: SearchRequest):
    try:
        return {'results': internet_search(payload.query)}
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post('/generate')
def generate(payload: SearchRequest, db: Session = Depends(get_db)):
    return generate_content(db, prompt=payload.query)
