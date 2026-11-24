# -*- coding: utf-8 -*-
from PySide6.QtCore import QObject, Signal
from models.data_model import DataModel
from models.ml_model import MLModel
from models.state_model import ModelState
from services.logger_service import LoggerService
from viewmodels.training_viewmodel import TrainingViewModel
from viewmodels.visualization_viewmodel import VisualizationViewModel
from viewmodels.prediction_viewmodel import PredictionViewModel


class MainViewModel(QObject):
    data_loaded = Signal()
    model_trained = Signal(str)
    model_loaded_from_file = Signal(str)
    error = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.logger = LoggerService()
        self.data_model = DataModel()
        self.ml_model = MLModel()
        self.state = ModelState()

        self.training_vm = TrainingViewModel(self.ml_model, self.logger)
        self.viz_vm = VisualizationViewModel(self.ml_model, self.logger)
        self.prediction_vm = PredictionViewModel(self.ml_model, self.logger)

    def load_default_data(self):
        try:
            ds = self.data_model.load_default()
            self.state.input_path = ds.source_path
            self.viz_vm.set_dataset(ds)
            self.prediction_vm.set_dataset(ds)
            self.logger.success(f"Данные загружены: {ds.source_path}")
            self.logger.info(f"   • объектов: {len(ds.raw)}, признаков: {ds.X.shape[1]}")
            self.data_loaded.emit()
            return ds
        except Exception as e:
            self.logger.error(f"Ошибка загрузки данных: {e}")
            self.error.emit("Ошибка", f"Не удалось загрузить данные:\n{e}")
            return None

    def load_custom_data(self, content: bytes, filename: str) -> bool:
        """Загрузка пользовательского датасета через бота."""
        try:
            ok = self.data_model.load_from_bytes(content, filename)
            if not ok or self.data_model.dataset is None:
                self.error.emit("Ошибка загрузки", "Не удалось разобрать файл данных")
                return False

            ds = self.data_model.dataset
            self.state.input_path = ds.source_path
            self.viz_vm.set_dataset(ds)
            self.prediction_vm.set_dataset(ds)
            self.ml_model._model = None
            self.ml_model._y_pred = None
            self.logger.success(f"Загружены данные: {filename} ({len(ds.raw)} строк)")
            self.data_loaded.emit()
            return True
        except Exception as e:
            self.logger.error(f"Ошибка загрузки файла: {e}")
            self.error.emit("Ошибка загрузки", str(e))
            return False

    def build_olap(self, measure: str, row_dim: str, aggfunc: str = 'mean'):
        """Построение OLAP-куба."""
        ds = self.data_model.dataset
        if ds is None:
            return None
        from services.olap_engine import OLEngine
        pivot = OLEngine.build_cube(ds.raw, measure, row_dim, aggfunc)
        return OLEngine.render_heatmap(pivot, measure, row_dim, aggfunc)

    def train(self, model_type: str, params: dict):
        self.state.model_type = model_type
        self.state.params = params
        self.logger.info(f"Выбрана модель: {model_type}")
        ds = self.data_model.dataset
        if ds is None:
            self.error.emit("Ошибка", "Данные не загружены")
            return None
        return self.training_vm.start_training_sync(ds, model_type, params)

    def on_training_finished(self):
        try:
            path = self.ml_model.save()
            self.logger.success(f"Модель сохранена: {path}")
            self.model_trained.emit(path)
            return path
        except Exception as e:
            self.logger.error(f"Не удалось сохранить: {e}")
            return None

    def load_model_from_file(self, path: str):
        try:
            self.ml_model.load(path)
            ds = self.data_model.dataset
            if ds is not None:
                self.ml_model.set_last_X_test(ds.X_test)
                self.ml_model.set_feature_names(ds.X.columns)
                self.ml_model.predict(ds.X_test)
            self.state.loaded_model_path = path
            self.logger.success(f"Модель загружена: {path}")
            self.model_loaded_from_file.emit(path)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модели: {e}")
            self.error.emit("Ошибка", str(e))
            return False

    def visualize(self, viz_type: str, metric_name: str = "precision"):
        self.state.viz_type = viz_type
        self.state.current_metric = metric_name
        return self.viz_vm.build(viz_type, metric_name)
