# -*- coding: utf-8 -*-
from vkbottle.bot import Message

from vk_bot.keyboards.inline import main_menu_keyboard, params_model_keyboard, params_reset_keyboard
from vk_bot.handlers.common import _send, get_bot_logger
from services.hyperparams import (
    DEFAULT_PARAMS, format_params, parse_param_command, reset_params, set_param,
)

SHORT = {"Logistic Regression": "lr", "KNN": "knn", "Decision Tree": "dt"}
ALIASES = {v: k for k, v in SHORT.items()}
ALIASES.update({"logistic": "Logistic Regression", "logreg": "Logistic Regression", "tree": "Decision Tree"})

BUTTON_TO_MODEL = {
    "Параметры LR": "Logistic Regression",
    "Параметры KNN": "KNN",
    "Параметры DT": "Decision Tree",
}


async def handle_param_text(message: Message):
    """Команды вида 'lr C=0.5', 'reset lr', 'Сбросить lr'. Вызывается из общего роутера."""
    t = (message.text or "").strip()
    low = t.lower()

    if low.startswith("сбросить ") or low.startswith("reset "):
        alias = t.split(maxsplit=1)[-1].strip().lower()
        if alias == "all":
            for m in DEFAULT_PARAMS:
                reset_params(m)
            await _send(message, "Все параметры сброшены к значениям по умолчанию.", main_menu_keyboard())
            return
        model_type = ALIASES.get(alias)
        if model_type:
            reset_params(model_type)
            await _send(
                message,
                f"Параметры {model_type} сброшены:\n\n{format_params(model_type)}",
                main_menu_keyboard(),
            )
            get_bot_logger().command(f"Сброс параметров {model_type}", message.from_id)
            return

    parsed = parse_param_command(t)
    if parsed:
        model_type, params = parsed
        results = []
        for name, value in params.items():
            if name in DEFAULT_PARAMS[model_type]:
                ok = set_param(model_type, name, value)
                results.append(f"{name} = {value}" if ok else f"{name}: неверное значение (см. «допустимо»)")
            else:
                results.append(f"{name}: неизвестный параметр")
        await _send(
            message,
            f"Гиперпараметры {model_type} обновлены:\n" + "\n".join(results)
            + f"\n\nИтого:\n{format_params(model_type)}",
            main_menu_keyboard(),
        )
        get_bot_logger().command(f"Изменение параметров {model_type}", message.from_id, params)


def register_handlers(bot):
    @bot.on.message(text=["/params", "Параметры"])
    async def cmd_show_params(message: Message):
        text = (
            "Выберите модель для изменения гиперпараметров"
        )
        await _send(message, text, params_model_keyboard())

    @bot.on.message(text=list(BUTTON_TO_MODEL))
    async def cmd_param_model(message: Message):
        model_type = BUTTON_TO_MODEL[message.text.strip()]
        text = (
            f"Гиперпараметры {model_type}\n\n"
            f"{format_params(model_type)}\n\n"
            f"Изменить: {SHORT[model_type]} имя=значение\n"
            f"Сбросить: reset {SHORT[model_type]}"
        )
        await _send(message, text, params_reset_keyboard(model_type))
