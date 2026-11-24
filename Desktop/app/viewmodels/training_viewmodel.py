"""ViewModel вкладки обучения"""

from PySide6.QtCore import QObject, Signal, QThread
from models.ml_model import MLModel
from models.data_model import Dataset
from services.logger_service import LoggerService


class TrainingWorker(QThread):
    progress = Signal(int)
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, ml_model: MLModel, dataset: Dataset, model_type: str, params: dict):
        super().__init__()
        self.ml_model = ml_model
        self.dataset = dataset
        self.model_type = model_type
        self.params = params

    def run(self):
        try:
            self.progress.emit(10)
            self.ml_model.set_last_X_test(self.dataset.X_test)
            self.ml_model.set_feature_names(self.dataset.X.columns)
            y_pred = self.ml_model.train(
                self.model_type,
                self.dataset.X_train, self.dataset.y_train,
                self.dataset.X_test, self.params
            )
            self.progress.emit(100)
            self.finished.emit(y_pred)
        except Exception as e:
            self.error.emit(str(e))


class TrainingViewModel(QObject):
    progress = Signal(int)
    training_finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, ml_model: MLModel, logger: LoggerService):
        super().__init__()
        self.ml_model = ml_model
        self.logger = logger
        self._worker: TrainingWorker = None

    def start_training(self, dataset: Dataset, model_type: str, params: dict):
        self.logger.info(f"Начало обучения: {model_type}")
        for k, v in params.items():
            self.logger.info(f"   {k} = {v}")

        self._worker = TrainingWorker(self.ml_model, dataset, model_type, params)
        self._worker.progress.connect(self.progress.emit)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, y_pred):
        self.logger.success(f"Модель обучена. Предсказаний: {len(y_pred)}")
        self.training_finished.emit()

    def _on_error(self, err: str):
        self.logger.error(f"Ошибка обучения: {err}")
        self.error_occurred.emit(err)