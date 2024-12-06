from sqlalchemy import Engine, create_engine
from sqlalchemy.ext import asyncio as sa_async
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.automap import automap_base

from worker.config import PostgreSQL

config = PostgreSQL()


engine: Engine = create_engine(
    url=config.using_sync_driver,
    pool_size=config.pool_size,
    echo=config.debug,
    future=True,
)

Base = automap_base()
Base.prepare(autoload_with=engine)
Task = Base.classes.task
Product = Base.classes.product
async_engine: sa_async.AsyncEngine = sa_async.create_async_engine(
    url=config.using_async_driver,
    pool_size=config.pool_size,
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
