"""ViewModel вкладки предсказаний"""

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
        self.logger.info(f"Dataset установлен: {len(dataset.raw)} записей")

    def predict_new_row(self, features: dict):
        """Предсказание для новой строки с полным логированием"""
        self.logger.info(f"Начало предсказания для Id={features.get('Id', '?')}")
        self.logger.info(f"   Признаки: {', '.join([f'{k}={v}' for k, v in features.items() if k != 'Id'])}")

        # Валидация
        missing = [f for f in FEATURE_COLUMNS if f not in features]
        if missing:
            self.logger.error(f"✗ Отсутствуют поля: {', '.join(missing)}")
            self.message.emit("error", f"Отсутствуют поля: {', '.join(missing)}")
            return

        try:
            clean = {k: float(v) for k, v in features.items() if k in FEATURE_COLUMNS}
            self.logger.info(f"   Очищенные признаки: {len(clean)} значений")

            # Предсказание
            self.logger.info("   Вызов predict_single...")
            result = self.ml_model.predict_single(clean)
            self.logger.success(f"  Предсказан Type = {result['prediction']}")

            result['index'] = features.get('Id', 'нов.')
            result['features'] = clean
            result['true_label'] = None
            result['in_test_set'] = False
            result['correct'] = None

            # Оценка уверенности
            proba = result.get('probabilities')
            if proba:
                self.logger.info(f"   Получено {len(proba)} вероятностей")
                try:
                    evaluation = self.ml_model.evaluate_prediction(proba)
                    result['prediction_evaluation'] = evaluation
                    self.logger.success(
                        f"   Оценка уверенности: {evaluation['confidence']:.3f} "
                        f"(margin={evaluation['margin']:.3f}, entropy={evaluation['normalized_entropy']:.3f})"
                    )
                except Exception as e:
                    self.logger.warning(f"   Ошибка оценки уверенности: {e}")
                    result['prediction_evaluation'] = None
            else:
                self.logger.warning("   Вероятности не получены, используем fallback")
                result['prediction_evaluation'] = {
                    'confidence': 1.0,
                    'margin': 1.0,
                    'entropy': 0.0,
                    'normalized_entropy': 0.0,
                    'top_classes': [
                        {'class': int(result['prediction']), 'probability': 1.0}
                    ]
                }

            # Метрики модели
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
                    self.logger.info(f"   Метрики модели: accuracy={acc:.3f}")
                except Exception as e:
                    result['model_metrics'] = None
                    result['model_accuracy'] = None
                    self.logger.warning(f"   Не удалось вычислить метрики: {e}")
            else:
                result['model_metrics'] = None
                result['model_accuracy'] = None
                self.logger.info("   Dataset не установлен, метрики недоступны")

            self.logger.success(f"Предсказание завершено для Id={result['index']}")
            self.prediction_done.emit(result)

        except ValueError as e:
            self.logger.error(f"Некорректные значения: {e}")
            self.message.emit("error", f"Некорректные значения: {e}")
        except RuntimeError as e:
            self.logger.error(f"Ошибка модели: {e}")
            self.message.emit("warning", str(e))
        except Exception as e:
            self.logger.error(f"Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
            self.message.emit("error", str(e))