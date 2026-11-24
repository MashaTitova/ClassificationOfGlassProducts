# -*- coding: utf-8 -*-
from PySide6.QtCore import QObject, Signal
import numpy as np
from matplotlib.figure import Figure
from sklearn.metrics import ConfusionMatrixDisplay
from models.ml_model import MLModel
from models.data_model import Dataset
from services.logger_service import LoggerService
from sklearn.metrics import roc_curve, auc



class VisualizationViewModel(QObject):
    figure_ready = Signal(object)
    message = Signal(str, str)

    def __init__(self, ml_model: MLModel, logger: LoggerService):
        super().__init__()
        self.ml_model = ml_model
        self.logger = logger
        self._dataset: Dataset = None

    def set_dataset(self, dataset: Dataset):
        self._dataset = dataset

    def build(self, viz_type: str, metric_name: str = "precision") -> Figure:
        if not self.ml_model.is_trained:
            self.message.emit("warning", "Сначала обучите или загрузите модель")
            return None
        if self._dataset is None:
            self.message.emit("warning", "Данные не загружены")
            return None

        extra = f" (метрика: {metric_name})" if viz_type == "metrics" else ""
        self.logger.info(f"Построение: {viz_type}{extra}")

        try:
            if viz_type == "matrix":
                fig = self._build_matrix()
            elif viz_type == "coef":
                fig = self._build_coefficients()
            elif viz_type == "roc":
                fig = self._build_roc()
            elif viz_type == "metrics":
                fig = self._build_metrics(metric_name)
            else:
                return None
            self.figure_ready.emit(fig)
            self.logger.success(f"График '{viz_type}' построен")
            return fig
        except Exception as e:
            self.logger.error(f"Ошибка визуализации: {e}")
            self.message.emit("error", str(e))
            return None

    def _new_figure(self) -> Figure:
        fig = Figure(figsize=(8, 8), dpi=100)
        fig.patch.set_facecolor('#1a1b26')
        return fig

    def _build_matrix(self) -> Figure:
        fig = self._new_figure()
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1a1b26')
        display = ConfusionMatrixDisplay.from_predictions(
            self._dataset.y_test, self.ml_model.y_pred, ax=ax, cmap="Purples"
        )
        ax.set_title('Матрица ошибок', color='white', fontsize=14, pad=15)
        ax.tick_params(colors='white')
        for lbl in ax.get_xticklabels() + ax.get_yticklabels():
            lbl.set_color('white')
        if hasattr(display, 'im_'):
            cbar = display.im_.axes.figure.colorbar(display.im_, ax=ax)
            cbar.ax.yaxis.set_tick_params(color='white')
            for lbl in cbar.ax.yaxis.get_ticklabels():
                lbl.set_color('white')
        fig.tight_layout()
        return fig

    def _build_coefficients(self) -> Figure:
        res = self.ml_model.get_coefficients()
        if res is None:
            raise RuntimeError("Коэффициенты доступны только для Logistic Regression")
        coef, names, class_labels = res
        fig = self._new_figure()
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1a1b26')
        x = np.arange(len(names))
        colors = ['#7aa2f7', '#bb9af7', '#7dcfff', '#9ece6a', '#f7768e', '#e0af68', '#ff9e64']
        for i, c in enumerate(coef):
            label = f'Class {class_labels[i]}' if i < len(class_labels) else f'Class {i + 1}'
            ax.barh(x + i * 0.2, c, 0.2, label=label, color=colors[i % len(colors)])
        ax.set_yticks(x + 0.3)
        ax.set_yticklabels(names, fontsize=10, color='white')
        ax.set_xlabel('Коэффициент', color='white')
        ax.set_title('Коэффициенты логистической регрессии', color='white', fontsize=14)
        ax.legend(loc='best')
        ax.grid(axis='x', alpha=0.3, color='gray')
        ax.tick_params(colors='white')
        fig.tight_layout()
        return fig

    def _build_roc(self) -> Figure:
        fig = self._new_figure()
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1a1b26')
        colors = ['#7aa2f7', '#bb9af7', '#7dcfff', '#9ece6a',
                  '#f7768e', '#e0af68', '#ff9e64']

        try:
            # 1. Проверки состояния
            if self._last_X_test_is_missing():
                raise RuntimeError(
                    "X_test не установлен: обучите модель")

            y_true = np.asarray(self._dataset.y_test)
            if len(y_true) == 0:
                raise RuntimeError("Тестовая выборка пуста")

            y_score = self.ml_model.model.predict_proba(self.ml_model._last_X_test)
            classes = np.unique(y_true)
            if len(classes) < 2:
                raise RuntimeError(
                    "ROC требует минимум 2 класса в тестовой выборке")

            # 2. Классы модели могут не совпадать с классами y_test — берём пересечение
            model_classes = getattr(self.ml_model.model, 'classes_', None)
            if model_classes is not None:
                mask = np.isin(classes, model_classes)
                classes = classes[mask]
                if len(classes) < 2:
                    raise RuntimeError(
                        "Классы теста и модели не пересекаются")

            from sklearn.preprocessing import label_binarize
            y_bin = label_binarize(y_true, classes=classes)

            plotted = 0
            for i, cls in enumerate(classes):
                if i >= y_bin.shape[1] or i >= y_score.shape[1]:
                    continue
                col_true = y_bin[:, i]
                if col_true.sum() == 0:
                    continue
                fpr, tpr, _ = roc_curve(col_true, y_score[:, i])
                roc_auc = auc(fpr, tpr)
                if np.isnan(roc_auc):
                    continue
                ax.plot(fpr, tpr, lw=2, color=colors[i % len(colors)],
                        label=f'Class {cls} (AUC={roc_auc:.2f})')
                plotted += 1

            if plotted == 0:
                raise RuntimeError("Нет классов, пригодных для ROC")

            ax.plot([0, 1], [0, 1], '--', lw=1, color='gray')
            ax.set_xlim([0, 1]); ax.set_ylim([0, 1.05])
            ax.set_xlabel('FPR', color='white')
            ax.set_ylabel('TPR', color='white')
            ax.set_title('ROC-кривые (One-vs-Rest)', color='white', fontsize=14)
            ax.legend(loc="lower right")
            ax.grid(alpha=0.3, color='gray')
            ax.tick_params(colors='white')

        except Exception as e:
            self.logger.error(f"Ошибка ROC: {e}")
            ax.cla()
            ax.set_facecolor('#1a1b26')
            ax.text(0.5, 0.5, f"ROC недоступен:\n{e}",
                    transform=ax.transAxes, ha='center', va='center',
                    color='white', fontsize=12)
            ax.axis('off')

        fig.tight_layout()
        return fig

    def _last_X_test_is_missing(self) -> bool:
        return getattr(self.ml_model, '_last_X_test', None) is None

    def _build_metrics(self, metric_name: str) -> Figure:
        fig = self._new_figure()
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1a1b26')
        
        try:
            metrics = self.ml_model.per_class_metrics(self._dataset.y_test)
            classes = np.unique(np.concatenate([self._dataset.y_test, self.ml_model.y_pred]))
            
            METRIC_INFO = {
                'precision': ('Precision (Точность)', '#7aa2f7'),
                'recall':    ('Recall (Полнота)',     '#bb9af7'),
                'f1':        ('F1-score',             '#7dcfff'),
            }
            if metric_name not in METRIC_INFO:
                metric_name = 'precision'
            title, color = METRIC_INFO[metric_name]
            
            # --- ЗАЩИТА ОТ NaN И ДЛИНЫ ---
            values_raw = metrics.get(metric_name, )
            
            # Приводим к numpy и заменяем NaN на 0, чтобы график не ломался
            values = np.array(values_raw, dtype=float)
            values = np.nan_to_num(values, nan=0.0)
            
            # Обрезаем или дополняем, если длины не совпадают (частая проблема при отсутствии классов)
            if len(values) > len(classes):
                values = values[:len(classes)]
            elif len(values) < len(classes):
                # Если классов больше, чем значений (редкий кейс), дополняем нулями
                values = np.pad(values, (0, len(classes) - len(values)), constant_values=0)
            # -----------------------------

            x = np.arange(len(classes))
            bars = ax.bar(x, values, 0.5, color=color)
            
            for bar, v in zip(bars, values):
                # Показываем только 2 знака, если значение не 0
                label_text = f'{v:.2f}' if v > 0 else ''
                ax.annotate(label_text,
                            xy=(bar.get_x() + bar.get_width() / 2, v),
                            xytext=(0, 5), textcoords="offset points",
                            ha='center', va='bottom', color='white')

            ax.set_xticks(x)
            ax.set_xticklabels([str(c) for c in classes], fontsize=10, color='white')
            ax.set_ylabel('Значение', color='white')
            ax.set_title(f'{title}', color='white', fontsize=14)
            ax.grid(axis='y', alpha=0.3, color='gray')
            ax.tick_params(colors='white')
            
        except Exception as e:
            self.logger.error(f"Критическая ошибка при построении метрик: {e}")
            # Возвращаем пустую фигуру с текстом ошибки, чтобы не было None
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Ошибка данных:\n{str(e)}", transform=ax.transAxes, 
                    ha='center', va='center', color='white', fontsize=12)
            ax.axis('off')
            
        fig.tight_layout()
        return fig