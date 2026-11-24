# -*- coding: utf-8 -*-
import json
import random

from vkbottle.bot import Message

from vk_bot.keyboards.inline import main_menu_keyboard
from vk_bot.handlers.state import reset_state
from viewmodels.main_viewmodel import MainViewModel
from services.bot_logger import bot_logger as _bot_logger

_vm = MainViewModel()
_vm.load_default_data()


def get_vm() -> MainViewModel:
    return _vm


def get_bot_logger():
    return _bot_logger


def keyboard_to_json(keyboard):
    if keyboard is None:
        return None
    if isinstance(keyboard, dict):
        return json.dumps(keyboard, ensure_ascii=False)
    if hasattr(keyboard, "get_json"):
        try:
            return json.dumps(json.loads(keyboard.get_json()), ensure_ascii=False)
        except Exception as e:
            print(f"[KB] конвертация не удалась: {e}; клавиатура: {type(keyboard)}")
            return None
    if isinstance(keyboard, str):
        return keyboard
    print(f"[KB] неизвестный тип клавиатуры: {type(keyboard)}")
    return str(keyboard)



async def _send(message: Message, text: str, keyboard=None):
    if keyboard is None:
        keyboard = main_menu_keyboard()
    kb_json = keyboard_to_json(keyboard)
    params = {
        "peer_id": message.peer_id,
        "message": text,
        "random_id": random.randint(0, 2 ** 31 - 1),
    }
    if kb_json:
        params["keyboard"] = kb_json
    try:
        await message.ctx_api.messages.send(**params)
        print("[SEND] ok")
    except Exception:
        import traceback
        traceback.print_exc()
        print("[SEND] ОШИБКА")


HELP_TEXT = (
    "Справка GlassBot\n\n"
    "Загрузить данные — загрузить свой датасет\n"
    "OLAP — пошаговый анализ данных\n"
    "Параметры — просмотр и смена гиперпараметров модели\n"
    "Обучить — обучение модели\n"
    "Загрузить модель — загрузить сохранённую модель\n"
    "Предсказать — предсказание целевой переменной\n"
    "Визуализация — матрица ошибок, ROC, коэффициенты\n"
    "Метрики — precision / recall / F1\n"
    "Логи — прислать файл журнала сессии\n"
    "Справка — эта справка\n"
    "Выберите действие:"
)


def register_handlers(bot):
    @bot.on.message(text=["/start", "Старт", "Привет", "Начать", "начать", "привет", "старт"])
    async def cmd_start(message: Message):
        await _send_welcome(message)
        await _send(message, HELP_TEXT, main_menu_keyboard())
        get_bot_logger().info("Пользователь запустил бота", message.from_id)
        return True

    @bot.on.message(payload=[{"command": "start"}])
    async def cmd_start_payload(message: Message):
        await _send_welcome(message)
        await _send(message, HELP_TEXT, main_menu_keyboard())
        return True

    @bot.on.message(text=["/help", "Справка", "Помощь", "/menu", "Меню", "Главное меню"])
    async def cmd_help(message: Message):
        await _send(message, HELP_TEXT, main_menu_keyboard())
        return True

    @bot.on.message(text=["В меню", "Отмена", "ОТМЕНА", "в меню", "отмена", "Назад", "назад"])
    async def cmd_back(message: Message):
        from vk_bot.handlers.load_model import _clear_mode
        _clear_mode(message.peer_id)
        reset_state(message.peer_id)
        await _send(message, "Возврат в главное меню.", main_menu_keyboard())
        get_bot_logger().command("Возврат в меню", message.from_id)
        return True


async def _send_welcome(message: Message):
    vm = get_vm()
    ds = vm.data_model.dataset

    if ds:
        text = (
            "Добро пожаловать в GlassBot\n\n"
            "Датасет загружен:\n"
            f"Объектов: {len(ds.raw)}\n"
            f"Признаков: {ds.X.shape[1]}\n"
            f"Классов: {sorted(ds.y.unique().tolist())}\n\n"
            f"Первые 5 строк:\n{vm.data_model.preview(5)}\n\n"
        )
    else:
        text = "Не удалось загрузить данные. Проверьте наличие glassData.txt"

    await _send(message, text, main_menu_keyboard())
