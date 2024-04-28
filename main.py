import asyncio
import time

from config import config
from modules.notifier import notifier
from modules.worker import Worker
from modules.database import get_session
from utils.load import load_devices_info


async def main():
    while True:
        workers: list[Worker] = []

        for device in load_devices_info().sensors:
            async for session in get_session():
                workers.append(Worker(device_info=device, db=session))

        tasks = [worker.run() for worker in workers]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
