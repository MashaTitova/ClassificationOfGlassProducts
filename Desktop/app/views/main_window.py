"""Главное окно приложения (View)"""

import os
import sys
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QWidget, QFileDialog, QMessageBox,
    QVBoxLayout, QGraphicsDropShadowEffect,
    QMenuBar, QTableWidgetItem
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QColor, QKeySequence, QAction, QShortcut, QCloseEvent

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


from styles import DARK_STYLE
from views.ui_main_window import Ui_MainWindow
from views.widgets.log_panel import LogPanel
from views.widgets.prediction_panel import PredictionPanel
from viewmodels.main_viewmodel import MainViewModel
from views.widgets.olap_panel import OlapPanel


class GlassApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Classification of Glass Products")
        self.resize(1100, 800)
        self.setMinimumSize(1000, 750)

        self.setStyleSheet(DARK_STYLE)

        # ViewModel
        self.vm = MainViewModel()

        # UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Помощник для предсказаний
        self.prediction_helper = PredictionPanel()

        # OLAP-анализ
        self.olap_panel = OlapPanel(self.vm.olap_vm)
        self.ui.tabWidget.addTab(self.olap_panel, 'OLAP-анализ')

        # Меню
        self._add_menu_bar()

        # Лог-панель
        self.log_panel = LogPanel()
        self.layout().addWidget(self.log_panel)

        # Тени
        self._add_shadows()

        self._setup_shortcuts()

        # Подключение сигналов
        self._connect_signals()

        # Загрузка данных
        self.vm.load_default_data()

    def _setup_shortcuts(self):
        """Горячие клавиши приложения"""

        # F2 — сброс параметров к значениям по умолчанию
        shortcut_reset = QShortcut(QKeySequence("F2"), self)
        shortcut_reset.activated.connect(self._on_reset_defaults)

        # F3 — сохранить лог сессии в JSON
        shortcut_save_log = QShortcut(QKeySequence("F3"), self)
        shortcut_save_log.activated.connect(self._on_save_log)

    def _on_save_log(self):
        """Сохраняет лог сессии в JSON по нажатию F3"""
        try:
            log_path = self.vm.logger.save_to_json(self.vm.data_model.project_root)
            self.vm.logger.success(f"Лог сохранён: {log_path}")
            QMessageBox.information(
                self,
                "Лог сохранён",
                f"Сессия записана в файл:\n{log_path}",
            )
        except Exception as e:
            self.vm.logger.error(f"Ошибка сохранения лога: {e}")
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сохранить лог:\n{e}",
            )

    def _add_menu_bar(self):
        self.menu_bar = QMenuBar(self)
        help_menu = self.menu_bar.addMenu("Справка")

        help_action = QAction("Справка пользователя", self)
        help_action.setShortcut(QKeySequence("F1"))
        help_action.triggered.connect(self._show_help)
        help_menu.addAction(help_action)

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        self.layout().insertWidget(0, self.menu_bar)

    def _add_shadows(self):
        def add_shadow(widget, color="#7aa2f7", blur=18, offset=3):
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(blur)
            shadow.setColor(QColor(color))
            shadow.setOffset(0, offset)
            widget.setGraphicsEffect(shadow)

        add_shadow(self.ui.btn_create, "#7aa2f7", 20)
        add_shadow(self.ui.btn_recreate, "#bb9af7", 20)
        add_shadow(self.ui.btn_visualize, "#7dcfff", 15)
        add_shadow(self.ui.btn_clear, "#f7768e", 15)
        add_shadow(self.ui.btn_select_model, "#7dcfff", 12)
        add_shadow(self.ui.btn_predict_new, "#9ece6a", 15)

    def _on_reset_defaults(self):
        """Сбрасывает гиперпараметры текущей модели к значениям по умолчанию"""
        if self.ui.radio_lr.isChecked():
            model_type = "Logistic Regression"
            defaults = self.vm.reset_params_to_defaults(model_type)
            self.ui.spin_lr_c.setValue(defaults['C'])
            # solver — найти индекс в комбобоксе
            idx = self.ui.combo_lr_solver.findText(defaults['solver'])
            if idx >= 0:
                self.ui.combo_lr_solver.setCurrentIndex(idx)
            self.ui.spin_lr_max_iter.setValue(defaults['max_iter'])
            idx_w = self.ui.combo_lr_class_weight.findText(defaults['class_weight'])
            if idx_w >= 0:
                self.ui.combo_lr_class_weight.setCurrentIndex(idx_w)

        elif self.ui.radio_knn.isChecked():
            model_type = "KNN"
            defaults = self.vm.reset_params_to_defaults(model_type)
            self.ui.spin_knn_k.setValue(defaults['n_neighbors'])
            # weights
            weights_text = "По расстоянию (distance)" if defaults['weights'] == 'distance' else "Равные веса (uniform)"
            idx = self.ui.combo_knn_weights.findText(weights_text)
            if idx >= 0:
                self.ui.combo_knn_weights.setCurrentIndex(idx)
            # metric
            metric_map = {
                'euclidean': "Евклидово (euclidean)",
                'manhattan': "Манхэттенское (manhattan)",
                'minkowski': "Минковского (minkowski)"
            }
            metric_text = metric_map.get(defaults['metric'], "Евклидово (euclidean)")
            idx_m = self.ui.combo_knn_metric.findText(metric_text)
            if idx_m >= 0:
                self.ui.combo_knn_metric.setCurrentIndex(idx_m)

        else:
            model_type = "Decision Tree"
            defaults = self.vm.reset_params_to_defaults(model_type)
            self.ui.spin_dt_max_depth.setValue(defaults['max_depth'])
            self.ui.spin_dt_min_split.setValue(defaults['min_samples_split'])
            self.ui.spin_dt_min_leaf.setValue(defaults['min_samples_leaf'])

        self.vm.logger.info(f"Параметры {model_type} сброшены к значениям по умолчанию")

    def _connect_signals(self):
        # VM → View
        self.vm.data_loaded.connect(self._on_data_loaded)
        self.vm.model_trained.connect(self._on_model_trained)
        self.vm.model_loaded_from_file.connect(self._on_model_loaded)
        self.vm.error.connect(lambda t, m: QMessageBox.critical(self, t, m))

        self.vm.training_vm.progress.connect(self.ui.progress_bar.setValue)
        self.vm.training_vm.training_finished.connect(self.vm.on_training_finished)
        self.vm.training_vm.error_occurred.connect(
            lambda e: QMessageBox.critical(self, "Ошибка обучения", e)
        )

        self.vm.viz_vm.figure_ready.connect(self._show_figure)
        self.vm.viz_vm.message.connect(self._on_viz_message)

        self.vm.prediction_vm.prediction_done.connect(self._on_prediction_done)
        self.vm.prediction_vm.message.connect(self._on_prediction_message)

        self.vm.logger.log_added.connect(self.log_panel.add_entry)

        # View → VM
        self.log_panel.save_btn.clicked.connect(self._on_save_log)
        self.ui.btn_predict_new.clicked.connect(self._on_predict_new)
        self.ui.model_group.buttonClicked.connect(self._on_model_selected)
        self.ui.btn_change_input.clicked.connect(self._change_input_path)
        self.ui.btn_create.clicked.connect(self._create_model)
        self.ui.btn_recreate.clicked.connect(self._create_model)
        self.ui.btn_select_model.clicked.connect(self._select_model)
        self.ui.btn_visualize.clicked.connect(self._visualize)
        self.ui.btn_clear.clicked.connect(self._clear_area)

        self.ui.radio_viz_metrics.toggled.connect(self.ui.metric_row.setVisible)

        # Предсказания
        self.ui.btn_predict_new.clicked.connect(self._on_predict_new)
        self.ui.btn_reset_form.clicked.connect(self._on_reset_form)

        # Логирование параметров
        self.ui.spin_lr_c.valueChanged.connect(
            lambda v: self.vm.log_param_change("C", v))
        self.ui.combo_lr_solver.currentTextChanged.connect(
            lambda v: self.vm.log_param_change("solver", v))
        self.ui.spin_lr_max_iter.valueChanged.connect(
            lambda v: self.vm.log_param_change("max_iter", v))
        self.ui.combo_lr_class_weight.currentTextChanged.connect(
            lambda v: self.vm.log_param_change("class_weight", v))

        self.ui.spin_knn_k.valueChanged.connect(
            lambda v: self.vm.log_param_change("n_neighbors", v))
        self.ui.combo_knn_weights.currentTextChanged.connect(
            lambda v: self.vm.log_param_change("weights", v))
        self.ui.combo_knn_metric.currentTextChanged.connect(
            lambda v: self.vm.log_param_change("metric", v))

        self.ui.spin_dt_max_depth.valueChanged.connect(
            lambda v: self.vm.log_param_change("max_depth", v))
        self.ui.spin_dt_min_split.valueChanged.connect(
            lambda v: self.vm.log_param_change("min_samples_split", v))
        self.ui.spin_dt_min_leaf.valueChanged.connect(
            lambda v: self.vm.log_param_change("min_samples_leaf", v))

        self.ui.combo_metric.currentTextChanged.connect(
            lambda v: self.vm.logger.info(f"Метрика визуализации → {v}")
        )

    def _on_model_selected(self, button):
        if button == self.ui.radio_lr:
            self.ui.param_stack.setCurrentIndex(0)
            self.vm.log_model_selection("Logistic Regression")
        elif button == self.ui.radio_knn:
            self.ui.param_stack.setCurrentIndex(1)
            self.vm.log_model_selection("KNN")
        elif button == self.ui.radio_dt:
            self.ui.param_stack.setCurrentIndex(2)
            self.vm.log_model_selection("Decision Tree")

    def _on_data_loaded(self):
        self.ui.line_edit_input_path.setText(self.vm.state.input_path)
        # Обновляем таблицу предпросмотра на первой вкладке
        self._update_preview_table()

    def _update_preview_table(self):
        """Заполняет таблицу предпросмотра первыми 5 строками"""
        ds = self.vm.data_model.dataset
        if ds is None:
            return

        preview = ds.raw.head(5)
        self.ui.preview_table.setRowCount(len(preview))
        self.ui.preview_table.setColumnCount(len(preview.columns))
        self.ui.preview_table.setHorizontalHeaderLabels([str(c) for c in preview.columns])

        for r_idx, (_, row) in enumerate(preview.iterrows()):
            for c_idx, col in enumerate(preview.columns):
                val = row[col]
                text = "" if pd.isna(val) else str(val)
                item = QTableWidgetItem(text)
                if col == 'Type':
                    item.setForeground(QColor('#7dcfff'))
                    item.setFont(self.ui.preview_table.font())
                self.ui.preview_table.setItem(r_idx, c_idx, item)

        self.vm.logger.info(f"Предпросмотр: показано {len(preview)} строк из {len(ds.raw)}")

    def _change_input_path(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать файл с данными", self.vm.data_model.project_root,
            "Text files (*.txt);;CSV files (*.csv);;All files (*)"
        )
        if file_path:
            self.vm.load_data_from_file(file_path)

    def _get_params(self):
        if self.ui.radio_lr.isChecked():
            return {
                'C': self.ui.spin_lr_c.value(),
                'solver': self.ui.combo_lr_solver.currentText(),
                'max_iter': self.ui.spin_lr_max_iter.value(),
                'class_weight': None if self.ui.combo_lr_class_weight.currentText() == "None" else "balanced"
            }
        elif self.ui.radio_knn.isChecked():
            weights = "distance" if "distance" in self.ui.combo_knn_weights.currentText() else "uniform"
            metric = "euclidean"
            if "manhattan" in self.ui.combo_knn_metric.currentText():
                metric = "manhattan"
            elif "minkowski" in self.ui.combo_knn_metric.currentText():
                metric = "minkowski"
            return {
                'n_neighbors': self.ui.spin_knn_k.value(),
                'weights': weights,
                'metric': metric
            }
        else:
            max_d = self.ui.spin_dt_max_depth.value()
            return {
                'max_depth': None if max_d == 0 else max_d,
                'min_samples_split': self.ui.spin_dt_min_split.value(),
                'min_samples_leaf': self.ui.spin_dt_min_leaf.value()
            }

    def _create_model(self):
        if self.ui.radio_lr.isChecked():
            model_type = "Logistic Regression"
        elif self.ui.radio_knn.isChecked():
            model_type = "KNN"
        else:
            model_type = "Decision Tree"

        self.ui.progress_bar.setValue(0)
        self.vm.train(model_type, self._get_params())

    def _on_model_trained(self, path: str):
        QMessageBox.information(self, "Готово", f"Модель обучена и сохранена:\n{path}")

    def _select_model(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать модель", self.vm.data_model.project_root,
            "Model files (*.pkl);;All files (*)"
        )
        if file_path:
            self.vm.load_model_from_file(file_path)
            self.ui.line_edit_model_path.setText(file_path)

    def _on_model_loaded(self, path: str):
        QMessageBox.information(self, "Успех", "Модель загружена")

    def _visualize(self):
        if self.ui.radio_viz_matrix.isChecked():
            viz_type = "matrix"
        elif self.ui.radio_viz_coef.isChecked():
            viz_type = "coef"
        elif self.ui.radio_viz_roc.isChecked():
            viz_type = "roc"
        elif self.ui.radio_viz_metrics.isChecked():
            viz_type = "metrics"
        else:
            return

        metric = self.ui.combo_metric.currentText()
        self.vm.visualize(viz_type, metric)

    def _show_figure(self, fig):
        for i in reversed(range(self.ui.viz_layout.count())):
            w = self.ui.viz_layout.itemAt(i).widget()
            if w is not None:
                w.setParent(None)

        from PySide6.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(False)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #2f334d; border-radius: 6px;
                background-color: #1a1b26;
            }
        """)

        canvas = FigureCanvas(fig)
        canvas.setFixedSize(800, 800)
        scroll_area.setWidget(canvas)
        self.ui.viz_layout.addWidget(scroll_area)

    def _on_viz_message(self, level, msg):
        if level == "warning":
            QMessageBox.warning(self, "Внимание", msg)
        elif level == "error":
            QMessageBox.critical(self, "Ошибка", msg)

    def _clear_area(self):
        for i in reversed(range(self.ui.viz_layout.count())):
            w = self.ui.viz_layout.itemAt(i).widget()
            if w is not None:
                w.setParent(None)
        self.vm.logger.info("Область визуализации очищена")

    # Предсказания
    def _on_predict_new(self):
        """Обработчик кнопки 'Предсказать Type' с валидацией"""
        features, errors = self.prediction_helper.get_input_values(self.ui.input_table)

        if errors:
            msg = "⚠ Обнаружены проблемы во введённых данных:\n\n"
            msg += "\n".join(f"  • {e}" for e in errors)
            msg += "\n\nИсправьте значения и попробуйте снова."
            QMessageBox.warning(self, "Проверьте данные", msg)
            self.vm.logger.warning(f"Ошибки ввода: {'; '.join(errors)}")
            return

        if not features:
            QMessageBox.warning(self, "Внимание", "Таблица ввода пустая")
            return

        self.vm.prediction_vm.predict_new_row(features)

    def _on_reset_form(self):
        self.prediction_helper.reset_input_table(self.ui.input_table)
        self.ui.result_label.setText("Введите значения и нажмите «Предсказать Type»")
        self.ui.metrics_label.setText("Метрики модели появятся после предсказания")

    def _on_prediction_done(self, result: dict):
        """Обработка результата предсказания"""
        self.vm.logger.info(f"Получен результат предсказания: Type={result.get('prediction')}")
        
        # Результат предсказания
        self.prediction_helper.show_prediction_result(result, self.ui.result_label)
        self.vm.logger.info("   Отображён результат предсказания")

        # Оценка уверенности
        evaluation = result.get('prediction_evaluation')
        if evaluation is not None:
            self.prediction_helper.show_model_metrics(evaluation, self.ui.metrics_label)
            self.vm.logger.info("   Отображена оценка уверенности")
        else:
            self.ui.metrics_label.setText(
                "<b style='color:#bb9af7;font-size:14px'>Оценка уверенности предсказания:</b><br><br>"
                "<span style='color:#e0af68'>Недоступна (нет вероятностей)</span>"
            )
            self.vm.logger.warning("   Оценка уверенности недоступна")
    def _on_prediction_message(self, level, msg):
        if level == "warning":
            QMessageBox.warning(self, "Внимание", msg)
        elif level == "error":
            self.prediction_helper.show_error(msg, self.ui.result_label)

    # Справка
    def _show_help(self):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton

        help_text = """
        <h2 style="color: #7aa2f7;">Справка пользователя</h2>

        <p><b>Classification of Glass Products</b> — приложение для классификации
        типов стекла на основе физико-химических свойств.</p>

        <h3 style="color: #bb9af7;">Вкладка «Создание модели»</h3>
        <ul>
            <li><b>Изменить</b> — выбрать файл данных</li>
            <li><b>Предпросмотр</b> — первые 5 строк таблицы отображаются автоматически</li>
            <li>Выбор модели и её гиперпараметров</li>
            <li><b>Создать модель</b> — обучение и сохранение</li>
        </ul>

        <h3 style="color: #bb9af7;">Вкладка «Визуализация и анализ»</h3>
        <ul>
            <li>Загрузка обученной модели из файла <code>.pkl</code></li>
            <li>Типы графиков: коэффициенты, матрица ошибок, ROC-кривые, <b>метрики</b></li>
            <li>Метрики выводятся <b>по очереди</b>: precision, recall, f1</li>
        </ul>

        <h3 style="color: #bb9af7;">Вкладка «Предсказания»</h3>
        <ul>
            <li>Введите значения признаков в таблицу (Id, RI, Na, Mg, Al, Si, K, Ca, Ba, Fe)</li>
            <li>Нажмите <b>«Предсказать Type»</b> — модель вернёт предсказанный класс и вероятности</li>
            <li>Ниже отображаются метрики модели (precision, recall, f1, accuracy)</li>
        </ul>

        <h3 style="color: #bb9af7;">Журнал действий</h3>
        <p>Внизу окна — сворачиваемая панель со всеми действиями.</p>

         <h3 style="color: #bb9af7;">Горячие клавиши</h3>
        <ul>
            <li><b>F1</b> — открыть справку</li>
            <li><b>F2</b> — сбросить параметры модели к значениям по умолчанию</li>
            <li><b>F3</b> — сохранить журнал действий в JSON-файл</li>
        </ul>
        """

        dialog = QDialog(self)
        dialog.setWindowTitle("Справка пользователя")
        dialog.resize(600, 500)
        dialog.setStyleSheet("QDialog { background-color: #1a1b26; }")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(15, 15, 15, 15)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(help_text)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #24283b; color: #c0caf5;
                border: 1px solid #2f334d; border-radius: 6px;
                padding: 15px; font-size: 13px;
            }
            QTextEdit h2 { color: #7aa2f7; font-size: 18px; }
            QTextEdit h3 { color: #bb9af7; font-size: 15px; margin-top: 15px; }
            QTextEdit b { color: #7dcfff; }
            QTextEdit code {
                background-color: #1a1b26; padding: 2px 6px;
                border-radius: 3px; font-family: 'Consolas', monospace;
                color: #9ece6a;
            }
        """)
        layout.addWidget(text_edit)

        from PySide6.QtWidgets import QPushButton as QPB
        ok_btn = QPB("OK")
        ok_btn.setFixedSize(120, 40)
        ok_btn.clicked.connect(dialog.accept)
        layout.addWidget(ok_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        dialog.exec()

    def _show_about(self):
        QMessageBox.about(
            self, "О программе",
            "<b>Classification of Glass Products</b><br><br>"
            "Приложение для классификации типов стекла<br>"
            "с использованием алгоритмов машинного обучения.<br><br>"
            "<b>Модели:</b> Logistic Regression, KNN, Decision Tree<br>"
            "<b>Архитектура:</b> MVVM<br>"
            "<b>Версия:</b> 3.1<br>"
            "<b>Автор:</b> Титова Мария, 2026"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = GlassApp()
    window.show()
    sys.exit(app.exec())