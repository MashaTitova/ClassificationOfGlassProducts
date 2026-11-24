import os

from vkbottle.bot import Message

from vk_bot.keyboards.inline import main_menu_keyboard
from vk_bot.handlers.common import _send, get_bot_logger



def register_handlers(bot):
    @bot.on.message(text=["/logs", "Логи", "Логирование"])
    async def cmd_logs(message: Message):
        path = get_bot_logger().latest_log_file()
        if not path:
            await _send(message, "Лог-файл ещё не создан.", main_menu_keyboard())
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            await _send(message, f"Не удалось прочитать лог: {e}\nФайл: {path}",
                        main_menu_keyboard())
            return

        if len(content) > 3500:
            content = "...\n" + content[-3500:]

        await _send(message, f"Журнал сессии (текст):\n\n{content}", main_menu_keyboard())
