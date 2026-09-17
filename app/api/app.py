from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import chat_router
from app.infrastructure.database import init_db_engin, close_db_engine


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     init_engine()
#     get_dialogue_engine()
#     build_action_runner()
#     yield
#
#     close_engine()
#
#
# # 创建fastapi对象，注册路由
# app = FastAPI(description="智能客服系统",lifespan="lifespan")

app = FastAPI(description="智能客服系统")
app.include_router(chat_router)