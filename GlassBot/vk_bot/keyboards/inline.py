"""Клавиатуры для VK-бота"""

from vkbottle.tools import Keyboard, Text, KeyboardButtonColor



def main_menu_keyboard() -> Keyboard:
    kb = Keyboard(one_time=False, inline=False)
    kb.add(Text(label="Загрузить данные"), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text(label="OLAP"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text(label="Параметры"), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text(label="Обучить"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text(label="Загрузить модель"), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text(label="Предсказать"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text(label="Визуализация"), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text(label="Метрики"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text(label="Логи"), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text(label="Справка"), color=KeyboardButtonColor.SECONDARY)
    return kb


def model_selection_keyboard() -> Keyboard:
    kb = Keyboard(one_time=True, inline=False)
    kb.add(Text(label="Logistic Regression"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text(label="KNN"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text(label="Decision Tree"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text(label="В меню"), color=KeyboardButtonColor.SECONDARY)
    return kb


def params_model_keyboard() -> Keyboard:
    kb = Keyboard(one_time=True, inline=False)
    kb.add(Text(label="Параметры LR"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text(label="Параметры KNN"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text(label="Параметры DT"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text(label="В меню"), color=KeyboardButtonColor.SECONDARY)
    return kb


def params_reset_keyboard(model_type: str) -> Keyboard:
    short = {"Logistic Regression": "lr", "KNN": "knn", "Decision Tree": "dt"}
    kb = Keyboard(one_time=True, inline=False)
    kb.add(
        Text(label=f"Сбросить {short[model_type]}"),
        color=KeyboardButtonColor.NEGATIVE,
    )
    kb.row()
    kb.add(Text(label="В меню"), color=KeyboardButtonColor.SECONDARY)
    return kb


def viz_selection_keyboard() -> Keyboard:
    kb = Keyboard(one_time=True, inline=False)
    kb.add(Text(label="Матрица ошибок"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text(label="ROC-кривые"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text(label="Коэффициенты"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text(label="В меню"), color=KeyboardButtonColor.SECONDARY)
    return kb


def metric_selection_keyboard() -> Keyboard:
    kb = Keyboard(one_time=True, inline=False)
    kb.add(Text(label="Precision"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text(label="Recall"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text(label="F1-score"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text(label="В меню"), color=KeyboardButtonColor.SECONDARY)
    return kb


import json


def _grid_keyboard(cmd_prefix: str, items, cols=3):
    items = [str(t) for t in (items or [])][:9]  
    rows = []
    for i in range(0, len(items), cols):
        rows.append([
            {
                "action": {
                    "type": "text",
                    "label": t,
                    "payload": json.dumps({"cmd": cmd_prefix, "value": t}),
                }
            }
            for t in items[i:i + cols]
        ])
    rows.append([{
        "action": {"type": "text", "label": "В меню", "payload": json.dumps({"cmd": "menu"})},
    }])
    return {"inline": True, "buttons": rows}


def olap_measure_keyboard(measures=None):
    return _grid_keyboard("olap_measure", measures or ["Count"])


def olap_row_dim_keyboard(row_dims=None):
    return _grid_keyboard("olap_row", row_dims or [])


def olap_agg_keyboard():
    return _grid_keyboard("olap_agg", ["mean", "median", "std", "sum", "min", "max"])

def upload_hint_keyboard() -> Keyboard:
    kb = Keyboard(one_time=False, inline=False)
    kb.add(Text(label="В меню"), color=KeyboardButtonColor.SECONDARY)
    return kb
