# -*- coding: utf-8 -*-
from vkbottle.bot import Message

from vk_bot.keyboards.inline import main_menu_keyboard
from vk_bot.handlers.common import get_vm, _send, get_bot_logger

# peer_id -> список накопленных строк данных
_data_buffer: dict = {}


def load_text_data_sync(text: str, source: str) -> bool:
    try:
        vm = get_vm()
        ok = vm.load_custom_data(text.encode("utf-8"), source)
        print(f"[UPLOAD] load_custom_data({source}) -> {ok}")
        return ok
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False


async def load_text_data(message: Message, text: str):
    """Накапливает данные по частям. Завершение — ГОТОВО, сброс — ОТМЕНА."""
    peer_id = message.peer_id
    low = text.strip().lower()

    try:
        if low == "готово":
            lines = _data_buffer.pop(peer_id, None)
            from vk_bot.handlers.state import reset_state
            reset_state(peer_id)

            if not lines or len(lines) < 2:
                await _send(
                    message,
                    "Буфер пуст или слишком короткий. Начните заново: отправьте DATA.",
                    main_menu_keyboard(),
                )
                return

            ok = load_text_data_sync("\n".join(lines), "data_from_chat.txt")
            if not ok:
                await _send(
                    message,
                    "ДАННЫЕ НЕ ПРИНЯТЫ. Проверьте:\n"
                    "1. Первая строка — заголовок: ID,RI,Na,Mg,Al,Si,K,Ca,Ba,Fe,Type (Пример)\n"
                    "2. Значения разделены запятыми\n"
                    "3. Строк данных не меньше 10",
                    main_menu_keyboard(),
                )
                return

            vm = get_vm()
            ds = vm.data_model.dataset
            await _send(
                message,
                "ДАННЫЕ ЗАГРУЖЕНЫ\n\n"
                f"Получено блоков: {len(lines)}\n"
                f"Строк всего: {len(ds.raw)}\n"
                f"Классы (Type): {sorted(ds.y.unique().tolist())}\n\n"
                f"Первые 5 строк:\n{vm.data_model.preview(5)}\n\n"
                "Теперь вы можете построить OLAP куб или обучить модель",
                main_menu_keyboard(),
            )
            get_bot_logger().info(f"Загружены данные текстом ({len(ds.raw)} строк)", message.from_id)
            return

        # обычное сообщение — копим в буфер
        _data_buffer.setdefault(peer_id, []).append(text)
        n = len(_data_buffer[peer_id])
        print(f"[UPLOAD] буфер {peer_id}: {n} сообщений")
        await _send(
            message,
            f"Принято блоков: {n}. Продолжайте; когда закончите — ГОТОВО (или ОТМЕНА).",
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        await _send(message, f"Ошибка при приёме данных: {e}", main_menu_keyboard())


def register_handlers(bot):

    @bot.on.message(text=["/upload", "Загрузить данные"])
    async def cmd_upload_hint(message: Message):
        text = (
            "Загрузка своих данных\n\n"
            "Порядок:\n"
            "1. Отправьте сообщение DATA\n"
            "2. Пришлите данные:"
            "Первая строка — заголовок колонок:\n"
            "ID,RI,Na,Mg,Al,Si,K,Ca,Ba,Fe,Type (Пример)\n"
            "3. Когда закончите — отправьте ГОТОВО (сброс — ОТМЕНА)\n\n"
            "Пример первого сообщения:\n"
            "ID,RI,Na,Mg,Al,Si,K,Ca,Ba,Fe,Type\n"
            "1,1.52101,13.64,4.49,1.10,71.78,0.06,8.75,0.00,0.00,1\n"
            "2,1.51761,13.89,3.60,1.36,72.73,0.48,7.83,0.00,0.00,1\n\n"
            "Формат: разделитель — запятая; целые Type; десятичный разделитель - точка.\n\n"
            "После ГОТОВО бот покажет сводку и первые 5 строк"
        )
        await _send(message, text, main_menu_keyboard())
        get_bot_logger().command("Запрос загрузки данных", message.from_id)
