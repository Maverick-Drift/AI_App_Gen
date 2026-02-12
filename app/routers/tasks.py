from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Schedule, Task
from app.schemas import ScheduleCreate, TaskCreate
from app.services.logging_service import write_log
from app.services.scheduler import sync_schedules
from app.services.task_runner import TaskExecutionError, run_task

router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.post('')
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    write_log(db, action='task.create', details=f'Task {task.id} created')
    return task


@router.get('')
def list_tasks(db: Session = Depends(get_db), limit: int = 100):
    return db.query(Task).order_by(Task.created_at.desc()).limit(limit).all()


@router.post('/{task_id}/run')
def execute_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')

    try:
        return run_task(db, task)
    except TaskExecutionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/{task_id}/schedule')
def schedule_task(task_id: int, payload: ScheduleCreate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')

    schedule = Schedule(task_id=task_id, **payload.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    sync_schedules()
    write_log(db, action='task.schedule', details=f'Schedule {schedule.id} added to task {task_id}')
    return schedule
