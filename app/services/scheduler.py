from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Schedule, Task
from app.services.logging_service import write_log
from app.services.task_runner import run_task

scheduler = BackgroundScheduler()


def run_task_job(task_id: int):
    db: Session = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id, Task.enabled.is_(True)).first()
        if not task:
            return
        run_task(db, task)
    finally:
        db.close()


def sync_schedules():
    db: Session = SessionLocal()
    try:
        scheduler.remove_all_jobs()
        schedules = db.query(Schedule).filter(Schedule.active.is_(True)).all()
        for schedule in schedules:
            if schedule.cron:
                trigger = CronTrigger.from_crontab(schedule.cron, timezone=schedule.timezone)
            elif schedule.run_once_at:
                trigger = DateTrigger(run_date=schedule.run_once_at, timezone=schedule.timezone)
            else:
                continue

            scheduler.add_job(run_task_job, trigger=trigger, args=[schedule.task_id], id=f'schedule-{schedule.id}', replace_existing=True)

        write_log(db, action='scheduler.sync', details=f'Synchronized {len(schedules)} schedule(s)')
    finally:
        db.close()
