import uvicorn

from app.api.dependencies import get_dialogue_engine, init_dialogue_engine
from app.config.config import settings
from app.infrastructure.database import init_engine
from app.task.action.builder import build_action_runner

if __name__=="__main__":
    init_engine()
    init_dialogue_engine()
    build_action_runner()
    uvicorn.run("api.app:app",
                host=settings.app_host,
                port=settings.app_port)