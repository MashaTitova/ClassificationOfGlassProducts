# -*- coding: utf-8 -*-
import os

from vkbottle.bot import Message
from vkbottle.tools import Keyboard, Text, KeyboardButtonColor

from vk_bot.keyboards.inline import main_menu_keyboard
from vk_bot.handlers.common import get_vm, _send, get_bot_logger

_awaiting: dict = {}
_page: dict = {}


def _models_dir() -> str:
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(root, "data", "models")


def _list_models() -> list:
    """Единый источник списка моделей: сортировка по времени создания, новые сверху."""
    d = _models_dir()
    if not os.path.isdir(d):
        return []
    files = [f for f in os.listdir(d) if f.endswith(".pkl")]
    files.sort(key=lambda f: os.path.getmtime(os.path.join(d, f)), reverse=True)
    return files


PER_PAGE = 6  


def _model_list_keyboard(total: int, page: int = 0) -> Keyboard:
    start = page * PER_PAGE
    end = min(start + PER_PAGE, total)
    kb = Keyboard(one_time=True, inline=False)

    shown = 0
    for i in range(start, end):
        kb.add(Text(label=str(i + 1)), color=KeyboardButtonColor.PRIMARY)
        shown += 1
        if shown % 3 == 0:
            kb.row()
    if shown % 3 != 0:
        kb.row()

    if page > 0:
        kb.add(Text(label="◀ Назад"), color=KeyboardButtonColor.SECONDARY)
    if end < total:
        kb.add(Text(label="Ещё ▶"), color=KeyboardButtonColor.SECONDARY)
    kb.add(Text(label="В меню"), color=KeyboardButtonColor.SECONDARY)
    return kb


async def show_page(message: Message, page: int):
    """Показывает страницу списка моделей: текст + клавиатура с навигацией."""
    models = _list_models()
    if not models:
        await _send(message,
            "Сохранённых моделей не найдено. Сначала обучите модель.",
            main_menu_keyboard())
        return

    max_page = (len(models) - 1) // PER_PAGE
    page = max(0, min(page, max_page))
    _page[message.peer_id] = page
    _awaiting[message.peer_id] = True  

    start = page * PER_PAGE
    end = min(start + PER_PAGE, len(models))

    lines = [f"{i}. {name}" for i, name in enumerate(models, 1) if start <= i - 1 < end]
    more_hint = ("\n\nЕсть ещё варианты — нажмите «Ещё ▶»." if end < len(models)
                 else "\n\nБольше моделей нет.")

    await _send(
        message,
        f"Выберите модель по номеру кнопки.\n"
        f"Показаны {start + 1}–{end} из {len(models)}:\n\n"
        + "\n".join(lines) + more_hint,
        _model_list_keyboard(len(models), page),
    )


def _clear_mode(peer_id: int):
    """Выход из режима выбора модели (используется и из cmd_back)."""
    _awaiting.pop(peer_id, None)
    _page.pop(peer_id, None)


def register_handlers(bot):
    @bot.on.message(text=["/load", "Загрузить модель"])
    async def cmd_load_menu(message: Message):
        print(f"[LOAD] найдено моделей: {len(_list_models())} в {_models_dir()}")
        await show_page(message, 0)
        get_bot_logger().command("Меню загрузки модели", message.from_id)

    @bot.on.message(text=["Ещё ▶"])
    async def next_page(message: Message):
        current = _page.get(message.peer_id, 0)
        await show_page(message, current + 1)

    @bot.on.message(text=["◀ Назад"])
    async def prev_page(message: Message):
        current = _page.get(message.peer_id, 0)
        await show_page(message, current - 1)

    @bot.on.message(text=[str(i) for i in range(1, 10)])
    async def pick_model(message: Message):
        if _awaiting.get(message.peer_id) is not True:
            return  

        models = _list_models()
        n = int(message.text.strip())
        if n < 1 or n > len(models):
            await _send(message, "Нет модели с таким номером — выберите из списка выше.")
            return

        filename = models[n - 1] 
        _clear_mode(message.peer_id)
        path = os.path.join(_models_dir(), filename)

        vm = get_vm()
        if vm.load_model_from_file(path):
            await _send(
                message,
                f"Модель загружена: {filename}\n\nТеперь доступны предсказания и визуализация.",
                main_menu_keyboard(),
            )
            get_bot_logger().info(f"Загружена модель: {filename}", message.from_id)
        else:
            await _send(message, "Не удалось загрузить модель. Файл повреждён?",
                        main_menu_keyboard())
