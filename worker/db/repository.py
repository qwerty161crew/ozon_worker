from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


class Repository:
    def __init__(self, connection: AsyncSession):
        self.connection = connection

    async def get(self, id: UUID | str, table):
        return await self.connection.get(table, id)

    async def insert(self, data: dict, model):
        if not self.check_table_entry(data["ozon_id"]):
            instance = model(**data)

            self.connection.add(instance=instance)
            await self.connection.flush()
            await self.connection.refresh(instance=instance)

            return instance

    async def update(self, id, models, data):
        instance = await self.get(id=id)
        if instance is None:
            return None

        for k, v in data.items():
            setattr(instance, k, v)

        self.connection.add(instance=instance)

        await self.connection.flush()
        await self.connection.refresh(instance=instance)

        return instance

    async def check_table_entry(self, id, table):
        return await self.connection.get(table, id)
