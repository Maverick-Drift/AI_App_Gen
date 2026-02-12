import json
import subprocess
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Task
from app.services.logging_service import write_log

SCRIPTS_DIR = Path('scripts').resolve()


class TaskExecutionError(Exception):
    pass


def _resolve_script(script_name: str) -> Path:
    script_path = (SCRIPTS_DIR / script_name).resolve()
    if SCRIPTS_DIR not in script_path.parents and script_path != SCRIPTS_DIR:
        raise TaskExecutionError('Script path escapes allowed scripts directory')
    if not script_path.exists():
        raise TaskExecutionError(f'Script not found: {script_name}')
    return script_path


def run_task(db: Session, task: Task) -> dict:
    if task.task_type != 'script':
        raise TaskExecutionError(f'Unsupported task_type: {task.task_type}')

    script_name = task.payload.get('script')
    args = task.payload.get('args', [])
    stdin_payload = task.payload.get('stdin', {})

    if not script_name:
        raise TaskExecutionError('Missing payload.script')

    script_path = _resolve_script(script_name)
    cmd = ['python', str(script_path), *[str(arg) for arg in args]]

    proc = subprocess.run(
        cmd,
        input=json.dumps(stdin_payload),
        text=True,
        capture_output=True,
        check=False,
    )

    result = {
        'return_code': proc.returncode,
        'stdout': proc.stdout,
        'stderr': proc.stderr,
    }

    task.last_status = 'success' if proc.returncode == 0 else 'failed'
    db.add(task)
    db.commit()

    write_log(
        db,
        action='task.run',
        details=f'Task {task.id} executed with return code {proc.returncode}',
        actor='scheduler',
        level='INFO' if proc.returncode == 0 else 'ERROR',
        extra_data={'task_id': task.id, 'task_name': task.name, **result},
    )
    return result
