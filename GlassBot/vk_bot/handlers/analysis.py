# -*- coding: utf-8 -*-
"""Хендлеры визуализации и метрик"""

import io

from vkbottle.bot import Message
from vkbottle.tools import PhotoMessageUploader

from vk_bot.keyboards.inline import (
    viz_selection_keyboard, metric_selection_keyboard, main_menu_keyboard,
)
from vk_bot.handlers.common import get_vm, _send, keyboard_to_json


async def _send_figure(message: Message, fig, caption: str):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, facecolor=fig.get_facecolor())
    buf.seek(0)
    buf.name = "plot.png"  

    try:
        uploader = PhotoMessageUploader(api=message.ctx_api)
        photo = await uploader.upload(buf, peer_id=message.peer_id)  # <-- peer_id

        await message.ctx_api.messages.send(
            peer_id=message.peer_id,
            message=caption,
            random_id=0,
            attachment=photo,
            keyboard=keyboard_to_json(main_menu_keyboard()),
        )
    except Exception as e:
        import traceback
        traceback.print_exc()   
        await _send(message, f"Ошибка отправки изображения: {e}", main_menu_keyboard())
    finally:
        import matplotlib.pyplot as plt
        plt.close(fig)



def register_handlers(bot):
    @bot.on.message(text=["/visualize", "Визуализация"])
    async def cmd_visualize(message: Message):
        await _send(message, "Выберите тип визуализации:", viz_selection_keyboard())
        return True

    @bot.on.message(text="Матрица ошибок")
    async def viz_matrix(message: Message):
        await _send_viz(message, "matrix", "Матрица ошибок")
        return True

    @bot.on.message(text="ROC-кривые")
    async def viz_roc(message: Message):
        await _send_viz(message, "roc", "ROC-кривые")
        return True

    @bot.on.message(text="Коэффициенты")
    async def viz_coef(message: Message):
        await _send_viz(message, "coef", "Коэффициенты")
        return True

    @bot.on.message(text=["/metrics", "Метрики"])
    async def cmd_metrics(message: Message):
        await _send(message, "Выберите метрику:", metric_selection_keyboard())
        return True

    @bot.on.message(text="Precision")
    async def metric_precision(message: Message):
        await _send_metric(message, "precision")
        return True

    @bot.on.message(text="Recall")
    async def metric_recall(message: Message):
        await _send_metric(message, "recall")
        return True

    @bot.on.message(text="F1-score")
    async def metric_f1(message: Message):
        await _send_metric(message, "f1")
        return True


async def _send_viz(message: Message, viz_type: str, caption: str):
    vm = get_vm()
    if not vm.ml_model.is_trained:
        await _send(message, "Сначала обучите или загрузите модель (кнопка «Обучить»).", main_menu_keyboard())
        return

    fig = vm.visualize(viz_type)
    if fig is None:
        await _send(message, f"Не удалось построить график «{caption}».", main_menu_keyboard())
        return
    await _send_figure(message, fig, caption)


async def _send_metric(message: Message, metric_name: str):
    vm = get_vm()
    fig = vm.visualize("metrics", metric_name)
    if fig is None:
        await _send(message, "Не удалось построить график.", main_menu_keyboard())
        return
    await _send_figure(message, fig, f"Метрика: {metric_name}")
