import os
import sys
from PySide6.QtCore import QObject, Signal
from models.olap_model import OLAPModel
from viewmodels.olap_viewmodel import OlapViewModel


_current_dir = os.path.dirname(os.path.abspath(__file__))
_app_dir = os.path.dirname(_current_dir)
_project_dir = os.path.dirname(_app_dir)
for _d in (_project_dir, _app_dir):
    if _d not in sys.path:
        sys.path.insert(0, _d)
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
        self.olap_model = OLAPModel()
        self.olap_vm = OlapViewModel(self.olap_model, self.logger)


    # Данные 
    def load_default_data(self):
        """Загружает данные по умолчанию (путь вычисляется в DataModel)"""
        try:
            ds = self.data_model.load_default() 
            self.state.input_path = ds.source_path
            self.viz_vm.set_dataset(ds)
            self.prediction_vm.set_dataset(ds)
            self.olap_vm.set_dataset(ds)
            self.logger.success(f"Данные загружены: {ds.source_path}")
            self.logger.info(f"объектов: {len(ds.raw)}, признаков: {ds.X.shape[1]}")
            self.data_loaded.emit()
        except Exception as e:
            self.logger.error(f"Ошибка загрузки данных: {e}")
            self.error.emit("Ошибка", f"Не удалось загрузить данные:\n{e}")

    def load_data_from_file(self, path: str):
        try:
            ds = self.data_model.load(path)
            self.state.input_path = path
            self.viz_vm.set_dataset(ds)
            self.prediction_vm.set_dataset(ds)
            self.olap_vm.set_dataset(ds)
            self.logger.success(f"Данные загружены: {path}")
            self.data_loaded.emit()
        except Exception as e:
            self.logger.error(f"Ошибка: {e}")
            self.error.emit("Ошибка", str(e))

    # Обучение 
    def train(self, model_type: str, params: dict):
        self.state.model_type = model_type
        self.state.params = params
        self.logger.info(f"Выбрана модель: {model_type}")
        ds = self.data_model.dataset
        if ds is None:
            self.error.emit("Ошибка", "Данные не загружены")
            return
        self.training_vm.start_training(ds, model_type, params)

    def on_training_finished(self):
        try:
            path = self.ml_model.save() 
            self.logger.success(f"Модель сохранена: {path}")
            self.model_trained.emit(path)
        except Exception as e:
            self.logger.error(f"Не удалось сохранить: {e}")

    # Загрузка модели
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
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модели: {e}")
            self.error.emit("Ошибка", str(e))

    # Визуализация
    def visualize(self, viz_type: str, metric_name: str = "precision"):
        self.state.viz_type = viz_type
        self.state.current_metric = metric_name
        self.viz_vm.build(viz_type, metric_name)

    # Логирование UI-событий
    def log_model_selection(self, model_type: str):
        self.state.model_type = model_type
        self.logger.info(f"Переключение модели -> {model_type}")

    def log_param_change(self, param_name: str, value):
        self.logger.info(f"Параметр '{param_name}' = {value}")

    # Сброс параметров к значениям по умолчанию
    def reset_params_to_defaults(self, model_type: str) -> dict:
        """Возвращает словарь параметров по умолчанию для выбранной модели"""
        defaults = {
            "Logistic Regression": {
                'C': 1.0,
                'solver': 'lbfgs',
                'max_iter': 1000,
                'class_weight': 'None'
            },
            "KNN": {
                'n_neighbors': 5,
                'weights': 'uniform',
                'metric': 'euclidean'
            },
            "Decision Tree": {
                'max_depth': 0,  
                'min_samples_split': 2,
                'min_samples_leaf': 1
            }
        }
        return defaults.get(model_type, {})