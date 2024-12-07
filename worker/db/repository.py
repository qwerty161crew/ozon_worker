from uuid import UUID

from db import SessionFactory
from sqlalchemy.ext.asyncio import AsyncSession


class Repository:
    def __init__(self, session: SessionFactory):
        self.session = session

    async def get(self, id: UUID | str, table):
        async with self.session() as connection:
            return await connection.get(table, id)

    async def insert(self, id, data: dict, model):
        async with self.session() as connection:
            if not self.check_table_entry(id, model):
                instance = model(**data)

                connection.add(instance=instance)
                await connection.flush()
                await connection.refresh(instance=instance)

                return instance

    async def update(self, id, models, data):
        instance = await self.get(table=models, id=id)
        if instance is None:
            return None

        for k, v in data.items():
            setattr(instance, k, v)
        async with self.session() as connection:
            connection.add(instance=instance)

            await connection.flush()
            await connection.refresh(instance=instance)
            await connection.commit()
            return instance

    async def check_table_entry(self, id, table):
        return await self.get(table, id)

    async def get_or_create(self, data, model):
        instance = await self.get(model, **data)
        if instance:
            return instance
        else:
            async with self.session() as connection:
                instance = model(**data)
                connection.add(instance)
                await connection.commit()
            return instance


async def get_repository():
    return Repository(session=SessionFactory)
