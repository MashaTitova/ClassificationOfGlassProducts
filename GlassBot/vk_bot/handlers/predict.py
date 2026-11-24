# -*- coding: utf-8 -*-
from vkbottle.bot import Message

from vk_bot.keyboards.inline import main_menu_keyboard
from vk_bot.handlers.common import get_vm, _send, get_bot_logger
from vk_bot.handlers.state import set_state, reset_state, in_mode
from vk_bot.handlers.upload import _data_buffer

PREDICT_TRIGGERS = {"/predict", "predict", "предсказать", "предсказание", "Предсказать", "Предсказание"}


def _feature_info():
    """Список признаков и имя цели из текущего датасета."""
    ds = getattr(get_vm().data_model, "_dataset", None)
    if ds is None:
        return [], ""
    cols = list(getattr(ds, "feature_columns", None) or ds.X.columns)
    return cols, getattr(ds, "target", "")


def _looks_like_numbers(text: str) -> bool:
    parts = [p for p in text.split(",") if p.strip()]
    if not parts:
        return False
    for p in parts:
        try:
            float(p.strip())
        except ValueError:
            return False
    return True


async def _activate_predict(message: Message):
    print("[PREDICT] активация режима")
    vm = get_vm()
    if not vm.ml_model.is_trained:
        await _send(message, "Сначала обучите или загрузите модель.", main_menu_keyboard())
        return
    cols, target = _feature_info()
    if not cols:
        await _send(message, "Данные не загружены. Сначала загрузите данные и обучите модель.", main_menu_keyboard())
        return
    set_state(message.peer_id, "predict")
    example = ",".join("1.0" for _ in cols)
    await _send(
        message,
        "Режим предсказания активирован.\n\n"
        f"Отправьте {len(cols)} значений через запятую — по порядку колонок:\n"
        f"{', '.join(cols)}\n\n"
        f"Пример:\n{example}\n\n"
        f"Отмена режима: ОТМЕНА.",
        main_menu_keyboard(),
    )
    get_bot_logger().command("Активация предсказания", message.from_id)


async def _do_prediction(message: Message, text: str):
    print(f"[PREDICT] получены значения: {text!r}")
    try:
        values = [float(x.strip()) for x in text.split(",") if x.strip()]
    except ValueError:
        await _send(message, "Введите числа через запятую (см. формат выше).", main_menu_keyboard())
        return

    cols, target = _feature_info()
    if not cols:
        await _send(message, "Данные не загружены. Сначала загрузите данные и обучите модель.", main_menu_keyboard())
        return

    if len(values) != len(cols):
        await _send(
            message,
            f"Ожидалось {len(cols)} значений, получено {len(values)}.\n"
            f"Порядок колонок: {', '.join(cols)}",
            main_menu_keyboard(),
        )
        return

    features = dict(zip(cols, values))
    result = get_vm().prediction_vm.predict_new_row(features)

    if result is None:
        await _send(message, "Ошибка предсказания: модель не обучена.", main_menu_keyboard())
        return

    ev = result.get("prediction_evaluation", {})
    conf = ev.get("confidence", 0)
    conf_text = "Высокая" if conf >= 0.8 else "Средняя" if conf >= 0.5 else "Низкая"
    proba = result.get("probabilities", {})
    proba_text = "\n".join(f"  Class {c}: {p:.3f}" for c, p in sorted(proba.items()))

    await _send(
        message,
        "РЕЗУЛЬТАТ ПРЕДСКАЗАНИЯ\n\n"
        f"Предсказанный {target or 'Type'}: {result['prediction']}\n\n"
        f"Уверенность: {conf:.3f} ({conf_text})\n"
        f"Margin: {ev.get('margin', 0):.3f}\n"
        f"Энтропия: {ev.get('normalized_entropy', 0):.3f}\n\n"
        f"Вероятности:\n{proba_text}",
        main_menu_keyboard(),
    )
    get_bot_logger().prediction(message.from_id, features, result)


def register_handlers(bot):
    @bot.on.message(text=["/predict", "Предсказать"])
    async def cmd_predict(message: Message):
        print("[PREDICT] сработал точный фильтр")
        await _activate_predict(message)


async def predict_router(message: Message, text: str) -> bool:
    """Разбирает режимы: предсказание, данные текстом, гиперпараметры.
    True — сообщение обработано, False — пусть идёт дальше."""
    low = text.lower()
    try:
        if low in PREDICT_TRIGGERS:
            await _activate_predict(message)
            return True

        if low == "data":
            set_state(message.peer_id, "data_text")
            _data_buffer[message.peer_id] = []
            await _send(
                message,
                "Режим ввода данных.\n"
                "Шлите строки данных частями.\n"
                "Первая строка — заголовок:\n"
                "RI,Na,Mg,Al,Si,K,Ca,Ba,Fe,Type\n\n"
                "Когда закончите — отправьте ГОТОВО. Сброс — ОТМЕНА.",
            )
            return True

        if in_mode(message.peer_id, "data_text"):
            from vk_bot.handlers.upload import load_text_data
            await load_text_data(message, text)
            return True

        if in_mode(message.peer_id, "predict") and _looks_like_numbers(text):
            reset_state(message.peer_id)
            await _do_prediction(message, text)
            return True

        if low.startswith(("lr ", "knn ", "dt ", "logistic ", "logreg ", "tree ",
                           "reset ", "сбросить ")):
            from vk_bot.handlers.hyperparams import handle_param_text
            await handle_param_text(message)
            return True

        if _looks_like_numbers(text):
            await _send(
                message,
                "Похоже на значения признаков, но режим предсказания не активен.\n"
                "Нажмите «Предсказать» и отправьте значения ещё раз.",
                main_menu_keyboard(),
            )
            return True

        return False
    except Exception as e:
        import traceback
        traceback.print_exc()
        await _send(message, f"Внутренняя ошибка: {e}", main_menu_keyboard())
        return True
