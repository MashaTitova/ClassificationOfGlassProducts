# -*- coding: utf-8 -*-
"""Хранилище гиперпараметров + подсказки по допустимым значениям"""

DEFAULT_PARAMS = {
    "Logistic Regression": {"C": 1.0, "solver": "lbfgs", "max_iter": 1000, "class_weight": None},
    "KNN": {"n_neighbors": 5, "weights": "uniform", "metric": "euclidean"},
    "Decision Tree": {"max_depth": None, "min_samples_split": 2, "min_samples_leaf": 1},
}

# Подсказки: что можно ставить
PARAM_INFO = {
    "Logistic Regression": {
        "C": "положительное число, например 0.1 / 1 / 10 (меньше — сильнее регуляризация)",
        "solver": "lbfgs | liblinear | newton-cg | sag | saga",
        "max_iter": "целое число, 100-10000",
        "class_weight": "None (авто) | balanced",
    },
    "KNN": {
        "n_neighbors": "целое число 1-50 (число соседей)",
        "weights": "uniform | distance",
        "metric": "euclidean | manhattan | minkowski | chebyshev | cosine",
    },
    "Decision Tree": {
        "max_depth": "None (авто) | целое число 1-50",
        "min_samples_split": "целое число >= 2",
        "min_samples_leaf": "целое число >= 1",
    },
}

current_params = {m: dict(p) for m, p in DEFAULT_PARAMS.items()}


def get_params(model_type: str) -> dict:
    return dict(current_params.get(model_type, {}))


def _coerce(default, value):
    if value is None or str(value).strip().lower() in ("none", "null", ""):
        return None
    if default is None:
        try:
            return int(value)
        except (ValueError, TypeError):
            return str(value)
    if isinstance(default, int):
        return int(value)
    if isinstance(default, float):
        return float(value)
    return str(value)


def _validate(model_type: str, name: str, v) -> bool:
    if v is None:
        return name in ("class_weight", "max_depth")
    checks = {
        "C": lambda x: x > 0,
        "max_iter": lambda x: x >= 1,
        "n_neighbors": lambda x: x >= 1,
        "max_depth": lambda x: x >= 1,
        "min_samples_split": lambda x: x >= 2,
        "min_samples_leaf": lambda x: x >= 1,
        "solver": lambda x: x in ("lbfgs", "liblinear", "newton-cg", "sag", "saga"),
        "weights": lambda x: x in ("uniform", "distance"),
        "metric": lambda x: x in ("euclidean", "manhattan", "minkowski", "chebyshev", "cosine"),
        "class_weight": lambda x: x in ("balanced",),
    }
    check = checks.get(name)
    return check(v) if check else True


def set_param(model_type: str, param_name: str, value) -> bool:
    if model_type not in current_params or param_name not in DEFAULT_PARAMS[model_type]:
        return False
    try:
        v = _coerce(DEFAULT_PARAMS[model_type][param_name], value)
        if not _validate(model_type, param_name, v):
            return False
        current_params[model_type][param_name] = v
        return True
    except (ValueError, TypeError):
        return False


def reset_params(model_type: str):
    if model_type in DEFAULT_PARAMS:
        current_params[model_type] = dict(DEFAULT_PARAMS[model_type])


def format_params(model_type: str) -> str:
    lines = []
    for name, val in current_params.get(model_type, {}).items():
        shown = val if val is not None else "None (авто)"
        line = f"  {name}: {shown}"
        info = PARAM_INFO.get(model_type, {}).get(name)
        if info:
            line += f"\n      допустимо: {info}"
        lines.append(line)
    return "\n".join(lines)


import re

def parse_param_command(text: str):
    """Парсит: 'knn n_neighbors=5', 'knn n_neighbors = 5 weights = distance' и т. п."""
    parts = text.strip().split(None, 1)
    if not parts:
        return None

    model_map = {
        "lr": "Logistic Regression", "logistic": "Logistic Regression",
        "logreg": "Logistic Regression", "knn": "KNN",
        "dt": "Decision Tree", "tree": "Decision Tree",
    }
    model_type = model_map.get(parts[0].lower())
    if not model_type:
        return None

    rest = parts[1] if len(parts) > 1 else ""
    # имя = значение с любым числом пробелов вокруг знака равенства
    pairs = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^\s=]+)", rest)
    return model_type, dict(pairs) if pairs else None

