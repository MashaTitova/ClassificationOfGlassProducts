"""Единственный центральный роутер. Регистрируется последним."""

import json

from vkbottle.bot import Message

from vk_bot.keyboards.inline import main_menu_keyboard
from vk_bot.handlers.common import _send
from vk_bot.handlers.olap import olap_step


def register_handlers(bot):
    @bot.on.message()
    async def central_router(message: Message):
        try:
            payload = json.loads(message.get_payload_json()) if message.get_payload_json() else None
        except Exception:
            payload = None
        if isinstance(payload, dict) and payload.get("cmd") in ("load_model_next", "load_model_prev"):
            from vk_bot.handlers.load_model import show_page
            page = int(payload.get("page", 0))
            await show_page(message, page + 1 if payload["cmd"] == "load_model_next" else page - 1)
            return

        text = (message.text or "").strip()
        if not text:
            return
        print(f"[ROUTER] text={text[:60]!r}")
        try:
            if await olap_step(message, text):
                return

            from vk_bot.handlers.predict import predict_router
            if await predict_router(message, text):
                return

            await _send(
                message,
                "Не распознал команду. Напишите «Справка» или нажмите на кнопку.",
                main_menu_keyboard(),
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            await _send(message, f"Внутренняя ошибка: {e}", main_menu_keyboard())
