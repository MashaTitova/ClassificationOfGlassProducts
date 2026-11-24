"""ViewModel визуализации"""

from PySide6.QtCore import QObject, Signal
import numpy as np
from matplotlib.figure import Figure
from sklearn.metrics import ConfusionMatrixDisplay

from models.ml_model import MLModel
from models.data_model import Dataset
from services.logger_service import LoggerService


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

    def build(self, viz_type: str, metric_name: str = "precision"):
        if not self.ml_model.is_trained:
            self.message.emit("warning", "Сначала обучите или загрузите модель")
            return
        if self._dataset is None:
            self.message.emit("warning", "Данные не загружены")
            return

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
                return
            self.figure_ready.emit(fig)
            self.logger.success(f"График '{viz_type}' построен")
        except Exception as e:
            self.logger.error(f"Ошибка визуализации: {e}")
            self.message.emit("error", str(e))

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
        coef, names = res
        fig = self._new_figure()
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1a1b26')
        x = np.arange(len(names))
        colors = ['#7aa2f7', '#bb9af7', '#7dcfff', '#9ece6a', '#f7768e', '#e0af68', '#ff9e64']
        for i, c in enumerate(coef):
            ax.barh(x + i * 0.2, c, 0.2, label=f'Class {i+1}', color=colors[i % len(colors)])
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
        colors = ['#7aa2f7', '#bb9af7', '#7dcfff', '#9ece6a', '#f7768e', '#e0af68', '#ff9e64']
        for i, (cls, fpr, tpr, roc_auc) in enumerate(self.ml_model.roc_data(self._dataset.y_test)):
            ax.plot(fpr, tpr, lw=2, color=colors[i % len(colors)],
                    label=f'Class {cls} (AUC={roc_auc:.2f})')
        ax.plot([0, 1], [0, 1], '--', lw=1, color='gray')
        ax.set_xlim([0, 1]); ax.set_ylim([0, 1.05])
        ax.set_xlabel('FPR', color='white'); ax.set_ylabel('TPR', color='white')
        ax.set_title('ROC-кривые (One-vs-Rest)', color='white', fontsize=14)
        ax.legend(loc="lower right"); ax.grid(alpha=0.3, color='gray')
        ax.tick_params(colors='white')
        fig.tight_layout()
        return fig

    def _build_metrics(self, metric_name: str) -> Figure:
        """Строит одну выбранную метрику по классам"""
        fig = self._new_figure()
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1a1b26')

        metrics = self.ml_model.per_class_metrics(self._dataset.y_test)
        classes = np.unique(self._dataset.y_test)

        METRIC_INFO = {
            'precision': ('Precision (Точность)', '#7aa2f7'),
            'recall':    ('Recall (Полнота)',     '#bb9af7'),
            'f1':        ('F1-score',             '#7dcfff'),
        }
        if metric_name not in METRIC_INFO:
            metric_name = 'precision'
        title, color = METRIC_INFO[metric_name]
        values = metrics[metric_name]

        x = np.arange(len(classes))
        bars = ax.bar(x, values, 0.5, color=color)
        for bar, v in zip(bars, values):
            ax.annotate(f'{v:.3f}',
                        xy=(bar.get_x() + bar.get_width() / 2, v),
                        xytext=(0, 5), textcoords="offset points",
                        ha='center', va='bottom', color='white', fontsize=11)

        acc = self.ml_model.accuracy(self._dataset.y_test)
        ax.set_title(f'{title}  Accuracy: {acc:.3f}', color='white', fontsize=14, pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels([f'Class {int(c)}' for c in classes], color='white', fontsize=11)
        ax.set_ylabel('Значение', color='white')
        ax.set_ylim(0, 1.15)
        ax.grid(axis='y', alpha=0.3, color='gray')
        ax.tick_params(colors='white')
        fig.tight_layout()
        return fig