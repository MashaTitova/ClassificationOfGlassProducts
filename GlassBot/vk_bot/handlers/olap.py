import io

from vkbottle.bot import Message
from vkbottle.tools import PhotoMessageUploader

from vk_bot.keyboards.inline import (
    olap_measure_keyboard, olap_row_dim_keyboard, olap_agg_keyboard,
    main_menu_keyboard,
)
from vk_bot.handlers.common import get_vm, _send, get_bot_logger, keyboard_to_json
import pandas as pd

AGGS = ["mean", "median", "std", "sum", "min", "max"]

_olap_state: dict = {}


def _olap_lists(vm):
    """Меры и измерения строятся из колонок текущего датасета."""
    ds = vm.data_model.dataset
    cols = list(getattr(ds, "feature_columns", ds.X.columns))
    target = getattr(ds, "target", None) or str(ds.y.name)

    numeric = [c for c in cols if pd.api.types.is_numeric_dtype(ds.X[c])]
    measures = numeric + ["Count"]
    row_dims = [target] + [f"{c} (bins)" for c in numeric]
    return cols, target, measures, row_dims


def register_handlers(bot):
    @bot.on.message(text=["/olap", "OLAP"])
    async def cmd_olap(message: Message):
        vm = get_vm()
        ds = vm.data_model.dataset
        if ds is None:
            await _send(message, "Данные не загружены.", main_menu_keyboard())
            return
        cols, target, measures, row_dims = _olap_lists(vm)
        text = (
            "OLAP-анализ данных\n\n"
            f"Всего записей: {len(ds.raw)}\n"
            f"Признаков: {ds.X.shape[1]}\n"
            f"Классов: {sorted(ds.y.unique().tolist())}\n\n"
            "Шаг 1/3: выберите меру для агрегации:"
        )
        _olap_state[message.peer_id] = {"step": "measure"}
        await _send(message, text, olap_measure_keyboard(measures))
        get_bot_logger().command("OLAP старт", message.from_id)


async def olap_step(message: Message, text: str) -> bool:
    """Шаги OLAP-диалога. Возвращает True, если сообщение израсходовано.
    Вызывается только из центрального роутера."""
    st = _olap_state.get(message.peer_id)
    if st is None or not text:
        return False

    vm = get_vm()
    ds = vm.data_model.dataset
    if ds is None:
        _olap_state.pop(message.peer_id, None)
        return False

    cols, target, measures, row_dims = _olap_lists(vm)
    step = st["step"]

    if step == "measure":
        if text not in measures:
            return False
        st["measure"] = text
        st["step"] = "row"
        await _send(message, "Шаг 2/3: выберите измерение группировки:", olap_row_dim_keyboard(row_dims))
        return True

    if step == "row":
        if text not in row_dims:
            return False
        st["row_dim"] = text
        st["step"] = "agg"
        await _send(message, "Шаг 3/3: выберите функцию агрегации:", olap_agg_keyboard())
        return True

    if step == "agg":
        if text.lower() not in AGGS:
            return False
        measure, row_dim, agg = st["measure"], st["row_dim"], text.lower()
        _olap_state.pop(message.peer_id, None)
        try:
            fig = vm.build_olap(measure, row_dim, agg)
        except Exception as e:
            import traceback
            traceback.print_exc()
            await _send(message, f"Ошибка построения куба: {e}", main_menu_keyboard())
            return True
        if fig is None:
            await _send(message, "Не удалось построить куб.", main_menu_keyboard())
            return True

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=100, facecolor=fig.get_facecolor())
        buf.seek(0)
        try:
            uploader = PhotoMessageUploader(api=message.ctx_api)
            photo = await uploader.upload(buf)
            await message.ctx_api.messages.send(
                peer_id=message.peer_id,
                message=f"OLAP-куб\nМера: {measure}\nГруппировка: {row_dim}\nАгрегат: {agg}",
                random_id=0,
                attachment=photo,
                keyboard=keyboard_to_json(main_menu_keyboard()),
            )
            get_bot_logger().command(f"OLAP: {measure}/{row_dim}/{agg}", message.from_id)
        except Exception as e:
            await _send(message, f"Ошибка отправки: {e}", main_menu_keyboard())
        finally:
            import matplotlib.pyplot as plt
            plt.close(fig)
        return True

    return False
