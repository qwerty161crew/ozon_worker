from sqlalchemy import Engine, create_engine
from sqlalchemy.ext import asyncio as sa_async
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.automap import automap_base

from worker.config import config

Base = automap_base()
engine: Engine = create_engine(
    url=config.postgres.db_url,
    pool_size=config.postgres.pool_size,
    echo=config.debug,
    future=True,
)

Base.prepare(autoload_with=engine)
Task = Base
Product = Base
ProductType = Base

async_engine: sa_async.AsyncEngine = sa_async.create_async_engine(
    url=config.postgres.db_url,
    pool_size=config.postgres.pool_size,
    echo=config.debug,
    future=True,
)

SessionFactory = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=sa_async.AsyncSession,
)
