import base64
import hashlib
import mimetypes
from pathlib import Path
from uuid import uuid4

import httpx
from PIL import Image
from sqlalchemy.orm import Session

from app.config import settings
from app.models import MediaAsset
from app.services.logging_service import write_log


def _ensure_media_dir() -> Path:
    path = settings.media_storage_path
    path.mkdir(parents=True, exist_ok=True)
    return path


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _detect_dimensions(path: Path) -> tuple[int | None, int | None]:
    try:
        with Image.open(path) as img:
            return img.width, img.height
    except Exception:
        return None, None


def save_image_bytes(db: Session, content: bytes, filename_hint: str = 'image', mime_type: str = 'image/jpeg', source: str = 'manual_upload', extra_data: dict | None = None) -> MediaAsset:
    media_dir = _ensure_media_dir()
    extension = Path(filename_hint).suffix or mimetypes.guess_extension(mime_type) or '.bin'
    filename = f'{uuid4().hex}{extension}'
    full_path = media_dir / filename
    full_path.write_bytes(content)

    digest = _hash_bytes(content)
    width, height = _detect_dimensions(full_path)

    asset = MediaAsset(
        source=source,
        media_type='image',
        file_path=str(full_path),
        mime_type=mime_type,
        sha256=digest,
        width=width,
        height=height,
        extra_data=extra_data or {},
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    write_log(db, action='media.store', details=f'Media asset {asset.id} stored', extra_data={'asset_id': asset.id, 'sha256': digest, 'source': source})
    return asset


def describe_image_with_ollama(image_path: str, user_prompt: str) -> str:
    data = Path(image_path).read_bytes()
    img_b64 = base64.b64encode(data).decode('utf-8')

    payload = {
        'model': settings.ollama_vision_model,
        'prompt': user_prompt,
        'images': [img_b64],
        'stream': False,
    }

    with httpx.Client(timeout=90) as client:
        response = client.post(f'{settings.ollama_base_url}/api/generate', json=payload)
        response.raise_for_status()
        return response.json().get('response', '')


def generate_image_post_idea(db: Session, asset: MediaAsset, objective: str) -> dict:
    prompt = (
        'Analyze this image and provide: '
        '1) concise visual context, '
        '2) caption for social media, '
        '3) short TikTok/Reel idea, '
        '4) short YouTube video hook. '
        f'Objective/context from user: {objective}'
    )

    if settings.llm_provider == 'ollama':
        result_text = describe_image_with_ollama(asset.file_path, prompt)
    else:
        result_text = f'[stubbed multimodal output] {objective}'

    asset.extracted_context = result_text[:4000]
    db.add(asset)
    db.commit()

    write_log(db, action='media.analyze', details=f'Analyzed media asset {asset.id}', extra_data={'asset_id': asset.id})
    return {'asset_id': asset.id, 'analysis': result_text}


def download_whatsapp_media(media_id: str) -> tuple[bytes, str, str]:
    headers = {'Authorization': f'Bearer {settings.whatsapp_access_token}'}

    with httpx.Client(timeout=60) as client:
        meta_resp = client.get(f'https://graph.facebook.com/v21.0/{media_id}', headers=headers)
        meta_resp.raise_for_status()
        meta = meta_resp.json()

        media_url = meta.get('url', '')
        mime_type = meta.get('mime_type', 'application/octet-stream')
        if not media_url:
            raise ValueError('WhatsApp media URL not found')

        media_resp = client.get(media_url, headers=headers)
        media_resp.raise_for_status()
        content = media_resp.content

    extension = mimetypes.guess_extension(mime_type) or '.bin'
    filename_hint = f'whatsapp_{media_id}{extension}'
    return content, mime_type, filename_hint
