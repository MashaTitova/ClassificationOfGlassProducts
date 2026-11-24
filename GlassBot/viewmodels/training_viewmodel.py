# -*- coding: utf-8 -*-
from PySide6.QtCore import QObject, Signal
from models.ml_model import MLModel
from models.data_model import Dataset
from services.logger_service import LoggerService


class TrainingViewModel(QObject):
    progress = Signal(int)
    training_finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, ml_model: MLModel, logger: LoggerService):
        super().__init__()
        self.ml_model = ml_model
        self.logger = logger

    def start_training_sync(self, dataset: Dataset, model_type: str, params: dict):
        """Синхронное обучение для бота"""
        self.logger.info(f"Начало обучения: {model_type}")
        for k, v in params.items():
            self.logger.info(f"   • {k} = {v}")
        try:
            self.ml_model.set_last_X_test(dataset.X_test)
            self.ml_model.set_feature_names(dataset.X.columns)
            y_pred = self.ml_model.train(
                model_type,
                dataset.X_train, dataset.y_train,
                dataset.X_test, params
            )
            self.logger.success(f"Модель обучена. Предсказаний: {len(y_pred)}")
            self.training_finished.emit()
            return y_pred
        except Exception as e:
            self.logger.error(f"Ошибка обучения: {e}")
            self.error_occurred.emit(str(e))
            return None