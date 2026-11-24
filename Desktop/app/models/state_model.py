"""Модель состояния приложения"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class ModelState:
    model_type: str = "Logistic Regression"
    params: Dict[str, Any] = field(default_factory=dict)
    input_path: str = ""
    loaded_model_path: str = ""
    viz_type: str = "matrix"
    current_metric: str = "precision"