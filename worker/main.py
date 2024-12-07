import asyncio
import json
import traceback

import aio_pika
import aio_pika.abc
from aio_pika import connect_robust
from aio_pika.robust_connection import AbstractRobustConnection

from worker.config import config
from worker.db import Repository, get_repository
from worker.db.tables import Product, ProductType, Task
from worker.schema import Product as ProducPedantic


class Consumer:
    def __init__(self, host, port, user, password, repository: Repository):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connect: AbstractRobustConnection | None = None
        self.repository = repository

    async def create_connection(self):
        if self.connect is None:
            self.connect = await connect_robust(
                f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/",
            )

    async def close_connection(self):

        if self.connect is not None:
            await self.connect.close()

    async def __aenter__(self):
        await self.create_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_connection()

    async def listen(self, event_loop):
        """
        MessageBody
        {
            "job_id": UUID,
            "start_url": "https://www.ozon.ru/",
            "product_type": ""
        }
        """
        async with self.connect:
            queue_name = "save-parse"
            channel: aio_pika.abc.AbstractChannel = await self.connect.channel()
            queue: aio_pika.abc.AbstractQueue = await channel.get_queue(queue_name)
            types = []
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        result = message.body.decode()
                        items = json.loads(result)
                        print(items)
                        for key, value in items.items():
                            try:
                                for parse_items in value:
                                    product = ProducPedantic(**parse_items)
                                    if product.product_type:
                                        for type in product.product_type:
                                            type_instance = (
                                                await self.repository.get_or_create(
                                                    model=ProductType, data=type
                                                )
                                            )
                                            types.append(type_instance)
                                    await self.repository.insert(
                                        id=ProducPedantic.ozon_id,
                                        data=ProducPedantic,
                                        model=Product,
                                    )
                                await self.repository.update(
                                    models=Task,
                                    id=key,
                                    data={
                                        "id": key,
                                        "state": "completed",
                                        "message": "Sucsess",
                                    },
                                )
                            except Exception:
                                await self.repository.update(
                                    models=Task,
                                    id=key,
                                    data={
                                        "id": key,
                                        "state": "fail",
                                        "message": traceback.format_exc(),
                                    },
                                )


async def run_worker():
    loop = asyncio.get_event_loop()
    repository = await get_repository()
    consumer = Consumer(
        user=config.rabbit_mq.user,
        host=config.rabbit_mq.host,
        port=config.rabbit_mq.port,
        password=config.rabbit_mq.password,
        repository=repository,
    )

    async with consumer:
        await consumer.listen(loop)
        # loop.run_forever()
    # finally:
    #     loop.close()


if __name__ == "__main__":
    asyncio.run(run_worker(), debug=True)
