"""Хендлеры обучения модели"""

from vkbottle.bot import Message

from vk_bot.keyboards.inline import model_selection_keyboard, main_menu_keyboard
from vk_bot.handlers.common import get_vm, _send, get_bot_logger
from services.hyperparams import get_params


async def _train_model(message: Message, vm, model_type: str):
    params = get_params(model_type)
    await _send(message, f"Обучаю {model_type} с параметрами: {params}")

    y_pred = vm.train(model_type, params)
    success = y_pred is not None
    get_bot_logger().training(message.from_id, model_type, params, success)

    if success:
        path = vm.on_training_finished()
        text = (
            "Модель обучена\n\n"
            f"Тип: {model_type}\n"
            f"Предсказаний: {len(y_pred)}\n"
            f"Сохранена: {path}"
        )
        await _send(message, text, main_menu_keyboard())
    else:
        await _send(message, "Ошибка обучения", main_menu_keyboard())
    return True


def register_handlers(bot):
    @bot.on.message(text=["/train", "Обучить"])
    async def cmd_train(message: Message):
        await _send(message, "Выберите модель для обучения:", model_selection_keyboard())
        return True

    @bot.on.message(text="Logistic Regression")
    async def train_lr(message: Message):
        return await _train_model(message, get_vm(), "Logistic Regression")

    @bot.on.message(text="KNN")
    async def train_knn(message: Message):
        return await _train_model(message, get_vm(), "KNN")

    @bot.on.message(text="Decision Tree")
    async def train_dt(message: Message):
        return await _train_model(message, get_vm(), "Decision Tree")
