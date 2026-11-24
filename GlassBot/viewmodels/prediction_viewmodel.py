from PySide6.QtCore import QObject, Signal
import pandas as pd
import numpy as np
from models.ml_model import MLModel
from models.data_model import Dataset, FEATURE_COLUMNS
from services.logger_service import LoggerService


class PredictionViewModel(QObject):
    prediction_done = Signal(dict)
    message = Signal(str, str)

    def __init__(self, ml_model: MLModel, logger: LoggerService):
        super().__init__()
        self.ml_model = ml_model
        self.logger = logger
        self._dataset: Dataset = None

    def set_dataset(self, dataset: Dataset):
        self._dataset = dataset

    def predict_new_row(self, features: dict) -> dict:
        """Синхронное предсказание для бота"""
        self.logger.info(f"Предсказание для Id={features.get('Id', '?')}")
        if not self.ml_model.is_trained:
            self.message.emit("warning", "Модель не загружена")
            return None

        missing = [f for f in FEATURE_COLUMNS if f not in features]
        if missing:
            self.message.emit("error", f"Отсутствуют поля: {', '.join(missing)}")
            return None

        try:
            clean = {k: float(v) for k, v in features.items() if k in FEATURE_COLUMNS}
            result = self.ml_model.predict_single(clean)
            result['index'] = features.get('Id', 'нов.')
            result['features'] = clean

            proba = result.get('probabilities')
            if proba:
                result['prediction_evaluation'] = self.ml_model.evaluate_prediction(proba)
            else:
                result['prediction_evaluation'] = {
                    'confidence': 1.0, 'margin': 1.0,
                    'entropy': 0.0, 'normalized_entropy': 0.0,
                    'top_classes': [{'class': int(result['prediction']), 'probability': 1.0}]
                }

            if self._dataset is not None:
                try:
                    per_class = self.ml_model.per_class_metrics(self._dataset.y_test)
                    acc = self.ml_model.accuracy(self._dataset.y_test)
                    classes = np.unique(np.concatenate([self._dataset.y_test, self.ml_model.y_pred]))
                    result['model_metrics'] = {
                        'precision': {int(c): float(per_class['precision'][i]) for i, c in enumerate(classes)},
                        'recall':    {int(c): float(per_class['recall'][i]) for i, c in enumerate(classes)},
                        'f1':        {int(c): float(per_class['f1'][i]) for i, c in enumerate(classes)},
                    }
                    result['model_accuracy'] = float(acc)
                except Exception as e:
                    result['model_metrics'] = None
                    result['model_accuracy'] = None

            self.logger.success(f"Предсказан Type = {result['prediction']}")
            self.prediction_done.emit(result)
            return result
        except Exception as e:
            self.message.emit("error", str(e))
            return None