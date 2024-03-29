import asyncio
import time

from config import config
from modules.notifier import notifier
from modules.worker import Worker
from modules.database import get_session
from utils.load import load_devices_info


async def main():
    await notifier.greeting()

    while True:
        workers: list[Worker] = []

        try:
            for device in load_devices_info().sensors:
                async for session in get_session():
                    workers.append(Worker(device_info=device, db=session))

            tasks = [worker.run() for worker in workers]
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            await notifier.error_occured(str(e))
        finally:
            await asyncio.sleep(config.THREAD_SLEEPTIME)


if __name__ == "__main__":
    try:
        start_time = time.time()
        asyncio.get_event_loop().run_until_complete(main())
    finally:
        elapsed_time = time.time() - start_time
        asyncio.get_event_loop().run_until_complete(
            notifier.script_stopped(elapsed_time)
        )
