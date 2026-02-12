from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MediaAsset
from app.schemas import ImageAnalyzeByIdRequest
from app.services.media import generate_image_post_idea, save_image_bytes

router = APIRouter(prefix='/media', tags=['media'])


@router.post('/images')
async def upload_image(
    file: UploadFile = File(...),
    objective: str = Form(default='Create social post suggestions from this image.'),
    db: Session = Depends(get_db),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail='Empty file')

    asset = save_image_bytes(
        db,
        content=content,
        filename_hint=file.filename or 'image.jpg',
        mime_type=file.content_type or 'application/octet-stream',
        source='api_upload',
    )
    analysis = generate_image_post_idea(db, asset, objective)
    return {'asset': asset, 'analysis': analysis}


@router.post('/images/analyze')
def analyze_existing_image(payload: ImageAnalyzeByIdRequest, db: Session = Depends(get_db)):
    asset = db.query(MediaAsset).filter(MediaAsset.id == payload.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail='Media asset not found')
    return generate_image_post_idea(db, asset, payload.objective)


@router.get('/images')
def list_images(db: Session = Depends(get_db), limit: int = 100):
    return db.query(MediaAsset).order_by(MediaAsset.created_at.desc()).limit(limit).all()
