from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import ActionLog

router = APIRouter(tags=['system'])


@router.get('/health')
def health():
    return {'status': 'ok'}


@router.get('/settings/web')
def web_settings():
    return {
        'mode': settings.web_access_mode,
        'allowlist_domains': [d.strip() for d in settings.web_allowlist_domains.split(',') if d.strip()],
    }


@router.get('/logs')
def list_logs(db: Session = Depends(get_db), limit: int = 200):
    return db.query(ActionLog).order_by(ActionLog.created_at.desc()).limit(limit).all()
