from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class KnowledgeItem(Base):
    __tablename__ = 'knowledge_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(120), default='manual')
    category: Mapped[str] = mapped_column(String(120), default='general')
    structured_data: Mapped[dict] = mapped_column(JSON, default=dict)
    unstructured_text: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MediaAsset(Base):
    __tablename__ = 'media_assets'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(80), default='manual_upload')
    media_type: Mapped[str] = mapped_column(String(30), default='image')
    file_path: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[str] = mapped_column(String(120), default='')
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extracted_context: Mapped[str] = mapped_column(Text, default='')
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    task_type: Mapped[str] = mapped_column(String(50), default='script')
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_status: Mapped[str] = mapped_column(String(30), default='idle')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    schedules: Mapped[list['Schedule']] = relationship('Schedule', back_populates='task', cascade='all, delete-orphan')


class Schedule(Base):
    __tablename__ = 'schedules'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'))
    cron: Mapped[str] = mapped_column(String(120), default='')
    run_once_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default='UTC')
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    task: Mapped['Task'] = relationship('Task', back_populates='schedules')


class ActionLog(Base):
    __tablename__ = 'action_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    level: Mapped[str] = mapped_column(String(20), default='INFO')
    actor: Mapped[str] = mapped_column(String(80), default='system')
    action: Mapped[str] = mapped_column(String(200))
    details: Mapped[str] = mapped_column(Text, default='')
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WhatsappEvent(Base):
    __tablename__ = 'whatsapp_events'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    direction: Mapped[str] = mapped_column(String(10), default='inbound')
    from_number: Mapped[str] = mapped_column(String(40), default='')
    to_number: Mapped[str] = mapped_column(String(40), default='')
    body: Mapped[str] = mapped_column(Text, default='')
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
