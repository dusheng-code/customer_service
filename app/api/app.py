from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.dependencies import init_dialogue_engine
from app.api.routers.chat_router import chat_router
from app.infrastructure.database import init_db_engin, close_db_engine
from app.infrastructure.http_client import init_http_client, close_http_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_engin()
    init_http_client()
    init_dialogue_engine()
    yield  # FASTAPI 处理请求....
    await close_db_engine()  # 应用关闭的时候才执行到
    await  close_http_client()
#
#
# # 创建fastapi对象，注册路由
app = FastAPI(description="智能客服系统",lifespan=lifespan)

# app = FastAPI(description="智能客服系统")
app.include_router(chat_router)