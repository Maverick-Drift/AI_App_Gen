from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas import WhatsappOutboundMessage
from app.services.whatsapp import save_inbound_event, send_text_message

router = APIRouter(prefix='/whatsapp', tags=['whatsapp'])


@router.get('/webhook')
def verify_webhook(
    hub_mode: str = Query(alias='hub.mode'),
    hub_verify_token: str = Query(alias='hub.verify_token'),
    hub_challenge: str = Query(alias='hub.challenge'),
):
    if hub_mode == 'subscribe' and hub_verify_token == settings.whatsapp_verify_token:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail='Invalid verify token')


@router.post('/webhook')
async def inbound_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    event = save_inbound_event(db, payload)
    return {'status': 'received', 'event_id': event.id}


@router.post('/send')
def send_message(payload: WhatsappOutboundMessage, db: Session = Depends(get_db)):
    return send_text_message(db, payload.text)
