import asyncio
import time


from config import config
from utils.loader import format_duration, load_devices_info
from modules.notifier import notifier
from modules.logger import logger
from modules.worker import Worker
from modules.database import get_session

start_time = time.time()


async def main():
    logger.info("机房温湿度检测脚本启动")
    await notifier.greeting()

    while True:
        workers: list[Worker] = []

        for device in load_devices_info().devices:
            async for session in get_session():
                workers.append(Worker(device_info=device, db=session))

        try:
            for worker in workers:
                await worker.run()
        finally:
            for worker in workers:
                await worker.close()

        logger.info(f"轮询完成，休眠{config.THREAD_SLEEPTIME}秒")
        await asyncio.sleep(config.THREAD_SLEEPTIME)


async def onexit():
    end_time = time.time()
    duration = end_time - start_time
    await notifier.goodbye(duration=format_duration(int(duration)))
    logger.info("机房温湿度检测脚本关闭")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(onexit())
