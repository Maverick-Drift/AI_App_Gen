from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class KnowledgeCreate(BaseModel):
    source: str = 'manual'
    category: str = 'general'
    structured_data: dict[str, Any] = Field(default_factory=dict)
    unstructured_text: str = ''


class TaskCreate(BaseModel):
    name: str
    task_type: str = 'script'
    payload: dict[str, Any] = Field(default_factory=dict)


class ScheduleCreate(BaseModel):
    cron: str = ''
    run_once_at: datetime | None = None
    timezone: str = 'UTC'


class SearchRequest(BaseModel):
    query: str


class WhatsappOutboundMessage(BaseModel):
    text: str


class ImageAnalyzeRequest(BaseModel):
    objective: str = 'Create social post suggestions from this image.'


class ImageAnalyzeByIdRequest(BaseModel):
    asset_id: int
    objective: str = 'Create social post suggestions from this image.'
