import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError , HTTPException

from .common.middleware.ComAopMiddleware import AopMiddleware
from .common.exception.ComExceptionHandler import *

from .common import ComDatabase

from .rag.controller import IndexingController , ChatController

# Uvicorn 로거 설정 덮어쓰기
uvicorn_log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "sqlalchemy.engine": {"handlers": ["default"], "level": "INFO", "propagate": False},
    },
}
logging.config.dictConfig(uvicorn_log_config)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="My Agent"
    )

# CORS middleware 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin을 허용하려면 "*" 사용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)
app.add_middleware(AopMiddleware)

app.include_router(IndexingController.router , tags=["Indexing"])
app.include_router(ChatController.router , tags=["Chat"])

app.add_exception_handler(RequestValidationError, validationExceptionHandler)
app.add_exception_handler(HTTPException, httpExceptionHandler)

"""
@app.on_event("startup")
async def startup_event():
    logging.info("my_agent startup................")
    logging.info("my_agent db connection init................")
    ComDatabase.startupDBConnection()
    logging.info("my_agent db connection success................")
    logging.info("my_agent entity init................")
    async with ComDatabase.getDBConnection().begin() as conn:
        await conn.run_sync(ComDatabase.dbBase.metadata.create_all)
        
    async with ComDatabase.getDBConnection().begin() as conn:
        await conn.run_sync(EmbeddingModelEntity.__table__.create, checkfirst=True)
        await conn.run_sync(DocumentEntity.__table__.create, checkfirst=True)
    
    logging.info("my_agent entity init success................")
"""
    
@app.on_event("shutdown")
async def shutdown_event():
    await ComDatabase.shutdownDBConnection()

    
