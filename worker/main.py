import asyncio
import json

import aio_pika
import aio_pika.abc
from aio_pika import Message, connect_robust
from aio_pika.robust_connection import AbstractRobustConnection
from config import config
from schema import Product


class Consumer:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connect: AbstractRobustConnection | None = None

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
            queue: aio_pika.abc.AbstractQueue = await channel.get_queue("save-parse")
            products = []
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        result = message.body.decode()
                        items = json.loads(result)
                        for key, value in items.items():
                            for parse_items in value:
                                product = Product(**parse_items)
                                products.append(product)


async def run_worker():
    repository = ()
    loop = asyncio.get_event_loop()
    consumer = Consumer(
        user=config.rabbit_mq.user,
        host=config.rabbit_mq.host,
        port=config.rabbit_mq.port,
        password=config.rabbit_mq.password,
    )

    async with consumer:
        await consumer.listen(loop)
        # loop.run_forever()
    # finally:
    #     loop.close()


if __name__ == "__main__":
    asyncio.run(run_worker(), debug=True)
