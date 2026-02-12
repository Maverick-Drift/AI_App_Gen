from sqlalchemy.orm import Session

from app.config import settings
from app.models import WhatsappEvent
from app.services.logging_service import write_log
from app.services.media import download_whatsapp_media, generate_image_post_idea, save_image_bytes
import httpx


def save_inbound_event(db: Session, payload: dict):
    from_number = ''
    body = ''
    image_asset_id = None

    try:
        value = payload['entry'][0]['changes'][0]['value']
        message = value.get('messages', [{}])[0]
        from_number = message.get('from', '')
        body = message.get('text', {}).get('body', '')

        image_id = message.get('image', {}).get('id')
        if image_id:
            content, mime_type, filename_hint = download_whatsapp_media(image_id)
            asset = save_image_bytes(
                db,
                content=content,
                filename_hint=filename_hint,
                mime_type=mime_type,
                source='whatsapp_inbound',
                extra_data={'whatsapp_media_id': image_id, 'from': from_number},
            )
            image_asset_id = asset.id

            objective = body or 'Create caption and social content ideas from this image.'
            generate_image_post_idea(db, asset, objective)
    except (KeyError, IndexError, TypeError):
        pass

    event = WhatsappEvent(
        direction='inbound',
        from_number=from_number,
        to_number=settings.whatsapp_allowed_to,
        body=body,
        raw_payload=payload,
    )
    db.add(event)
    db.commit()

    write_log(
        db,
        action='whatsapp.inbound',
        details='Inbound WhatsApp event received',
        actor='whatsapp',
        extra_data={'from': from_number, 'body': body, 'image_asset_id': image_asset_id},
    )
    return event


def send_text_message(db: Session, text: str):
    if not settings.whatsapp_allowed_to:
        raise ValueError('WHATSAPP_ALLOWED_TO is not configured')

    url = f'https://graph.facebook.com/v21.0/{settings.whatsapp_phone_number_id}/messages'
    payload = {
        'messaging_product': 'whatsapp',
        'to': settings.whatsapp_allowed_to,
        'type': 'text',
        'text': {'body': text},
    }
    headers = {'Authorization': f'Bearer {settings.whatsapp_access_token}'}

    with httpx.Client(timeout=30) as client:
        response = client.post(url, json=payload, headers=headers)

    outbound = WhatsappEvent(
        direction='outbound',
        from_number=settings.whatsapp_phone_number_id,
        to_number=settings.whatsapp_allowed_to,
        body=text,
        raw_payload=payload,
    )
    db.add(outbound)
    db.commit()

    write_log(
        db,
        action='whatsapp.outbound',
        details=f'Outbound WhatsApp send status {response.status_code}',
        actor='whatsapp',
        level='INFO' if response.is_success else 'ERROR',
        extra_data={'response': response.text[:1000]},
    )
    response.raise_for_status()
    return {'status_code': response.status_code, 'response': response.json() if response.text else {}}
