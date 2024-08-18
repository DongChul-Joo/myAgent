from fastapi import HTTPException , Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker , Session
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession , create_async_engine
from functools import wraps
from .ComEnv import commonEnvs
from typing import AsyncIterable , Optional


__dbConnection = None

dbBase = declarative_base()

def startupDBConnection():
    global __dbConnection
    __dbConnection = create_async_engine(
        commonEnvs.DATABASE_URL,     
        pool_size=20,  # Maximum number of connections
        max_overflow=10,  # Maximum number of overflow connections
        pool_timeout=30,  # Maximum wait time for a connection
        pool_recycle=1800,  # Time to recycle a connection (in seconds)
        pool_pre_ping=True  # Test the connection before using it
    )
    
async def shutdownDBConnection():
    global __dbConnection
    if __dbConnection:
        await __dbConnection.dispose()
    
def getDBConnection():
    assert __dbConnection is not None
    return __dbConnection


#auto_flush가 비동기 동작으로 인해 제대로 반영되지 않음 , repo 레벨에서 db.flush() 호출해서 사용해야함
def Transactional( auto_flush=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            session = sessionmaker(bind=getDBConnection() , autoflush=auto_flush , expire_on_commit=False , class_=AsyncSession)
            async with session() as db:
                kwargs = {**kwargs, 'db': db}
                
                if db is None:
                    raise HTTPException(status_code=500, detail="DB Connection Failed")
            
                try:
                    async with db.begin():
                        response = await func(*args, **kwargs) 
                        return response
                except Exception as e:
                    raise e
        return wrapper
    return decorator

def SelfCommitTransactional( auto_flush=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            session = sessionmaker(bind=getDBConnection() , autoflush=auto_flush , expire_on_commit=False , class_=AsyncSession)
            async with session() as db:
                kwargs = {**kwargs, 'db': db}
                
                if db is None:
                    raise HTTPException(status_code=500, detail="DB Connection Failed")
            
                try:
                    response = await func(*args, **kwargs)
                    await db.commit() 
                    return response
                except Exception as e:
                    await db.rollback()
                    raise e
        return wrapper
    return decorator