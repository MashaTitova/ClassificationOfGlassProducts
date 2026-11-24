"""Точка входа VK-бота"""

import asyncio
import logging
import os
import sys

import matplotlib
matplotlib.use("Agg")  

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from vk_bot.bot import create_bot


async def main():
    token = os.getenv("VK_BOT_TOKEN")
    if not token:
        print("Ошибка: VK_BOT_TOKEN не найден в .env файле")
        return

    bot = create_bot(token)
    print("VK GlassBot запущен. Нажмите Ctrl+C для остановки.")

    try:
        await bot.run_polling()
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")


if __name__ == "__main__":
    asyncio.run(main())
