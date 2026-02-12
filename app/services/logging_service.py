from sqlalchemy.orm import Session

from app.models import ActionLog


def write_log(db: Session, action: str, details: str = '', actor: str = 'system', level: str = 'INFO', extra_data: dict | None = None):
    event = ActionLog(
        level=level,
        actor=actor,
        action=action,
        details=details,
        extra_data=extra_data or {},
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
