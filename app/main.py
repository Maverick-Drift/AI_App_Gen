from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routers import agent, knowledge, media, system, tasks, whatsapp
from app.services.scheduler import scheduler, sync_schedules

app = FastAPI(title='Desktop AI Automation Hub', version='0.2.0')


@app.on_event('startup')
def on_startup():
    settings.media_storage_path.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    scheduler.start()
    sync_schedules()


@app.on_event('shutdown')
def on_shutdown():
    if scheduler.running:
        scheduler.shutdown()


app.include_router(system.router)
app.include_router(knowledge.router)
app.include_router(tasks.router)
app.include_router(agent.router)
app.include_router(media.router)
app.include_router(whatsapp.router)
