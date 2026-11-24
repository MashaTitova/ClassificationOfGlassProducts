"""UI-конструктор главного окна (3 вкладки)"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QTabWidget, QStackedWidget, QRadioButton, QPushButton,
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
    QProgressBar, QSizePolicy, QButtonGroup, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont

from models.data_model import FEATURE_COLUMNS


class Ui_MainWindow:
    """Класс построения интерфейса"""

    def setupUi(self, mainWidget):
        main_layout = QVBoxLayout(mainWidget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        self.tabWidget = QTabWidget()
        self.tabWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.tabWidget, 1)

        font12 = QFont()
        font12.setPointSize(12)

        # ================= ВКЛАДКА 1: Создание модели =================
        self.tab1 = QWidget()
        tab1_layout = QVBoxLayout(self.tab1)
        tab1_layout.setContentsMargins(8, 8, 8, 8)
        tab1_layout.setSpacing(8)

        self.params_box = QGroupBox("Параметры модели")
        outer_layout = QVBoxLayout(self.params_box)
        outer_layout.setContentsMargins(15, 28, 15, 15)
        outer_layout.setSpacing(12)

        path_row = QHBoxLayout()
        path_row.setSpacing(10)
        
        self.lbl_path = QLabel("Входные данные:")
        self.lbl_path.setFixedWidth(120)
        path_row.addWidget(self.lbl_path)

        self.line_edit_input_path = QLineEdit()
        self.line_edit_input_path.setReadOnly(True)
        self.line_edit_input_path.setMinimumHeight(36)
        self.line_edit_input_path.setPlaceholderText("Файл не выбран")
        path_row.addWidget(self.line_edit_input_path, 1)

        self.btn_change_input = QPushButton("Изменить")
        self.btn_change_input.setFixedSize(140, 40)
        path_row.addWidget(self.btn_change_input)
        
        outer_layout.addLayout(path_row)

        model_row = QHBoxLayout()
        model_row.setSpacing(10)

        self.lbl_model = QLabel("Модель классификации:")
        self.lbl_model.setFixedWidth(160)
        model_row.addWidget(self.lbl_model)

        self.radio_lr = QRadioButton("Logistic Regression")
        self.radio_lr.setMinimumWidth(180)
        self.radio_lr.setChecked(True)
        self.radio_knn = QRadioButton("KNN")
        self.radio_knn.setMinimumWidth(120)
        self.radio_dt = QRadioButton("Decision Tree")
        self.radio_dt.setMinimumWidth(150)

        for r in (self.radio_lr, self.radio_knn, self.radio_dt):
            model_row.addWidget(r)
        model_row.addStretch(1)
        outer_layout.addLayout(model_row)

        self.model_group = QButtonGroup(mainWidget)
        self.model_group.addButton(self.radio_lr, 0)
        self.model_group.addButton(self.radio_knn, 1)
        self.model_group.addButton(self.radio_dt, 2)

        self.param_stack = QStackedWidget()
        self.param_stack.setMinimumHeight(250)

        # --- Страница 1: LR ---
        self.page_lr = QWidget()
        p1 = QVBoxLayout(self.page_lr)
        p1.setContentsMargins(0, 0, 0, 0)
        self.gb_lr = QGroupBox("Параметры модели")
        f1 = QFormLayout(self.gb_lr)
        f1.setContentsMargins(15, 20, 15, 15)
        f1.setSpacing(18)

        self.lbl_c = QLabel("Коэффициент регуляризации (C):")
        self.spin_lr_c = QDoubleSpinBox()
        self.spin_lr_c.setRange(0.01, 100.0)
        self.spin_lr_c.setValue(1.0)
        self.spin_lr_c.setSingleStep(0.1)
        self.spin_lr_c.setDecimals(2)
        self.spin_lr_c.setMinimumWidth(180)
        self.spin_lr_c.setMinimumHeight(38)
        self.spin_lr_c.setFont(font12)
        f1.addRow(self.lbl_c, self.spin_lr_c)

        self.lbl_solver = QLabel("Алгоритм оптимизации (solver):")
        self.combo_lr_solver = QComboBox()
        self.combo_lr_solver.addItems(["lbfgs", "newton-cg", "saga", "liblinear"])
        self.combo_lr_solver.setMinimumWidth(200)
        self.combo_lr_solver.setMinimumHeight(38)
        self.combo_lr_solver.setFont(font12)
        f1.addRow(self.lbl_solver, self.combo_lr_solver)

        self.lbl_iter = QLabel("Максимальное число итераций (max_iter):")
        self.spin_lr_max_iter = QSpinBox()
        self.spin_lr_max_iter.setRange(100, 10000)
        self.spin_lr_max_iter.setValue(3000)
        self.spin_lr_max_iter.setSingleStep(100)
        self.spin_lr_max_iter.setMinimumWidth(180)
        self.spin_lr_max_iter.setMinimumHeight(38)
        self.spin_lr_max_iter.setFont(font12)
        f1.addRow(self.lbl_iter, self.spin_lr_max_iter)

        self.lbl_weight = QLabel("Балансировка классов (class_weight):")
        self.combo_lr_class_weight = QComboBox()
        self.combo_lr_class_weight.addItems(["None", "balanced"])
        self.combo_lr_class_weight.setMinimumWidth(200)
        self.combo_lr_class_weight.setMinimumHeight(38)
        self.combo_lr_class_weight.setFont(font12)
        f1.addRow(self.lbl_weight, self.combo_lr_class_weight)

        p1.addWidget(self.gb_lr)
        self.param_stack.addWidget(self.page_lr)

        # --- Страница 2: KNN ---
        self.page_knn = QWidget()
        p2 = QVBoxLayout(self.page_knn)
        p2.setContentsMargins(0, 0, 0, 0)
        self.gb_knn = QGroupBox("Параметры модели")
        f2 = QFormLayout(self.gb_knn)
        f2.setContentsMargins(15, 20, 15, 15)
        f2.setSpacing(18)

        self.lbl_k = QLabel("Количество соседей (n_neighbors):")
        self.spin_knn_k = QSpinBox()
        self.spin_knn_k.setRange(1, 50)
        self.spin_knn_k.setValue(5)
        self.spin_knn_k.setMinimumWidth(180)
        self.spin_knn_k.setMinimumHeight(38)
        self.spin_knn_k.setFont(font12)
        f2.addRow(self.lbl_k, self.spin_knn_k)

        self.lbl_weights = QLabel("Веса соседей (weights):")
        self.combo_knn_weights = QComboBox()
        self.combo_knn_weights.addItems(["Равные веса (uniform)", "По расстоянию (distance)"])
        self.combo_knn_weights.setMinimumWidth(220)
        self.combo_knn_weights.setMinimumHeight(38)
        self.combo_knn_weights.setFont(font12)
        f2.addRow(self.lbl_weights, self.combo_knn_weights)

        self.lbl_metric = QLabel("Метрика расстояния (metric):")
        self.combo_knn_metric = QComboBox()
        self.combo_knn_metric.addItems(["Евклидово (euclidean)", "Манхэттенское (manhattan)", "Минковского (minkowski)"])
        self.combo_knn_metric.setMinimumWidth(220)
        self.combo_knn_metric.setMinimumHeight(38)
        self.combo_knn_metric.setFont(font12)
        f2.addRow(self.lbl_metric, self.combo_knn_metric)

        p2.addWidget(self.gb_knn)
        self.param_stack.addWidget(self.page_knn)

        # --- Страница 3: DT ---
        self.page_dt = QWidget()
        p3 = QVBoxLayout(self.page_dt)
        p3.setContentsMargins(0, 0, 0, 0)
        self.gb_dt = QGroupBox("Параметры модели")
        f3 = QFormLayout(self.gb_dt)
        f3.setContentsMargins(15, 20, 15, 15)
        f3.setSpacing(18)

        self.lbl_depth = QLabel("Максимальная глубина дерева (max_depth):")
        self.spin_dt_max_depth = QSpinBox()
        self.spin_dt_max_depth.setRange(0, 50)
        self.spin_dt_max_depth.setValue(5)
        self.spin_dt_max_depth.setMinimumWidth(180)
        self.spin_dt_max_depth.setMinimumHeight(38)
        self.spin_dt_max_depth.setFont(font12)
        self.spin_dt_max_depth.setSpecialValueText("Без ограничений (None)")
        f3.addRow(self.lbl_depth, self.spin_dt_max_depth)

        self.lbl_split = QLabel("Мин. объектов для разделения (min_samples_split):")
        self.spin_dt_min_split = QSpinBox()
        self.spin_dt_min_split.setRange(2, 20)
        self.spin_dt_min_split.setValue(2)
        self.spin_dt_min_split.setMinimumWidth(180)
        self.spin_dt_min_split.setMinimumHeight(38)
        self.spin_dt_min_split.setFont(font12)
        f3.addRow(self.lbl_split, self.spin_dt_min_split)

        self.lbl_leaf = QLabel("Мин. объектов в листе (min_samples_leaf):")
        self.spin_dt_min_leaf = QSpinBox()
        self.spin_dt_min_leaf.setRange(1, 10)
        self.spin_dt_min_leaf.setValue(1)
        self.spin_dt_min_leaf.setMinimumWidth(180)
        self.spin_dt_min_leaf.setMinimumHeight(38)
        self.spin_dt_min_leaf.setFont(font12)
        f3.addRow(self.lbl_leaf, self.spin_dt_min_leaf)

        p3.addWidget(self.gb_dt)
        self.param_stack.addWidget(self.page_dt)

        param_scroll = QScrollArea()
        param_scroll.setWidget(self.param_stack)
        param_scroll.setWidgetResizable(True)
        param_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        param_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        param_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #2f334d;
                border-radius: 6px;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1a1b26;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #565f89;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #7aa2f7;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        outer_layout.addWidget(param_scroll, 1)  # stretch=1 — занимает всё доступное место

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(28)
        self.progress_bar.setValue(0)
        outer_layout.addWidget(self.progress_bar)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(15)
        
        self.btn_create = QPushButton("Создать модель")
        self.btn_create.setObjectName("btn_create")
        self.btn_create.setMinimumHeight(50)
        btn_row.addWidget(self.btn_create, 1)  # stretch=1

        self.btn_recreate = QPushButton("Пересоздать модель")
        self.btn_recreate.setObjectName("btn_recreate")
        self.btn_recreate.setMinimumHeight(50)
        btn_row.addWidget(self.btn_recreate, 1)  # stretch=1
        
        outer_layout.addLayout(btn_row)

        # ===== ТАБЛИЦА ПРЕДПРОСМОТРА =====
        self.preview_box = QGroupBox("Предпросмотр данных (первые 5 строк)")
        preview_layout = QVBoxLayout(self.preview_box)
        preview_layout.setContentsMargins(15, 25, 15, 10)

        self.preview_table = QTableWidget()
        self.preview_table.setRowCount(0)
        self.preview_table.setColumnCount(0)
        self.preview_table.setFixedHeight(160)
        self.preview_table.setStyleSheet("""
            QTableWidget {
                background-color: #24283b;
                color: #c0caf5;
                gridline-color: #2f334d;
                border: 1px solid #2f334d;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #2f334d;
                color: #7aa2f7;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
        """)
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.preview_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        preview_layout.addWidget(self.preview_table)

        outer_layout.addWidget(self.preview_box)

        tab1_layout.addWidget(self.params_box)
        self.tabWidget.addTab(self.tab1, "Создание модели")

        # ================= ВКЛАДКА 2: Визуализация =================
        self.tab2 = QWidget()
        tab2_main_layout = QVBoxLayout(self.tab2)
        tab2_main_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area2 = QScrollArea()
        scroll_area2.setWidgetResizable(True)
        scroll_area2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        content_widget = QWidget()
        content_widget.setMinimumWidth(900)
        tab2_layout = QVBoxLayout(content_widget)
        tab2_layout.setContentsMargins(8, 8, 8, 8)
        tab2_layout.setSpacing(10)

        # Загрузка модели
        self.load_box = QGroupBox("Загрузить модель")
        self.load_box.setMinimumHeight(100)
        self.load_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        load_layout = QHBoxLayout(self.load_box)
        load_layout.setContentsMargins(15, 25, 15, 10)
        load_layout.setSpacing(10)

        self.line_edit_model_path = QLineEdit()
        self.line_edit_model_path.setReadOnly(True)
        self.line_edit_model_path.setMinimumHeight(38)
        self.line_edit_model_path.setPlaceholderText("Модель не выбрана")
        load_layout.addWidget(self.line_edit_model_path, 1)

        self.btn_select_model = QPushButton("Выбрать модель")
        self.btn_select_model.setObjectName("btn_select_model")
        self.btn_select_model.setFixedWidth(170)
        self.btn_select_model.setMinimumHeight(38)
        load_layout.addWidget(self.btn_select_model)
        tab2_layout.addWidget(self.load_box)

        # Алгоритмы визуализации
        self.viz_box = QGroupBox("Алгоритмы визуализации")
        self.viz_box.setMinimumHeight(90)
        self.viz_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        viz_layout = QHBoxLayout(self.viz_box)
        viz_layout.setContentsMargins(15, 25, 15, 10)
        viz_layout.setSpacing(20)

        self.radio_viz_coef = QRadioButton("Коэффициенты")
        self.radio_viz_coef.setObjectName("radio_viz_coef")

        self.radio_viz_matrix = QRadioButton("Матрица ошибок")
        self.radio_viz_matrix.setObjectName("radio_viz_matrix")
        self.radio_viz_matrix.setChecked(True)

        self.radio_viz_roc = QRadioButton("ROC-кривые")
        self.radio_viz_roc.setObjectName("radio_viz_roc")

        self.radio_viz_metrics = QRadioButton("Метрики модели")
        self.radio_viz_metrics.setObjectName("radio_viz_metrics")

        for r in (self.radio_viz_coef, self.radio_viz_matrix, self.radio_viz_roc, self.radio_viz_metrics):
            r.setMinimumWidth(140)
            r.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            viz_layout.addWidget(r)
        viz_layout.addStretch(1)
        tab2_layout.addWidget(self.viz_box)

        # Выбор метрики
        self.metric_row = QWidget()
        metric_layout = QHBoxLayout(self.metric_row)
        metric_layout.setContentsMargins(15, 0, 15, 0)
        metric_layout.addWidget(QLabel("Выберите метрику:"))
        self.combo_metric = QComboBox()
        self.combo_metric.addItems(["precision", "recall", "f1"])
        self.combo_metric.setMinimumWidth(160)
        metric_layout.addWidget(self.combo_metric)
        metric_layout.addStretch()
        self.metric_row.setVisible(False)
        tab2_layout.addWidget(self.metric_row)

        # Кнопки визуализации
        btn_row2 = QHBoxLayout()
        btn_row2.setSpacing(15)
        self.btn_visualize = QPushButton("Визуализировать")
        self.btn_visualize.setObjectName("btn_visualize")
        self.btn_visualize.setMinimumHeight(42)
        self.btn_visualize.setFixedWidth(280)
        btn_row2.addWidget(self.btn_visualize)

        self.btn_clear = QPushButton("Очистить область")
        self.btn_clear.setObjectName("btn_clear")
        self.btn_clear.setMinimumHeight(42)
        self.btn_clear.setFixedWidth(280)
        btn_row2.addWidget(self.btn_clear)
        tab2_layout.addLayout(btn_row2)

        # Область графика
        self.visualization_area = QWidget()
        self.visualization_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.visualization_area.setMinimumSize(QSize(400, 300))
        self.viz_layout = QVBoxLayout(self.visualization_area)
        self.viz_layout.setContentsMargins(2, 2, 2, 2)
        tab2_layout.addWidget(self.visualization_area, 1)

        tab2_layout.addStretch(1)
        scroll_area2.setWidget(content_widget)
        tab2_main_layout.addWidget(scroll_area2)
        self.tabWidget.addTab(self.tab2, "Визуализация и анализ")

        # ================= ВКЛАДКА 3: Предсказания =================
        self.tab3 = QWidget()
        tab3_layout = QVBoxLayout(self.tab3)
        tab3_layout.setContentsMargins(8, 8, 8, 8)
        tab3_layout.setSpacing(10)

        # Таблица ввода
        self.input_box = QGroupBox("Введите значения признаков для предсказания Type")
        input_layout = QVBoxLayout(self.input_box)
        input_layout.setContentsMargins(15, 25, 15, 15)

        self.input_table = QTableWidget()
        self.input_table.setRowCount(1)
        self.input_table.setColumnCount(len(FEATURE_COLUMNS) + 1)
        headers = ['Id'] + FEATURE_COLUMNS
        self.input_table.setHorizontalHeaderLabels(headers)

        defaults = {
            'Id': '1', 'RI': '1.52101', 'Na': '13.64', 'Mg': '4.49',
            'Al': '1.10', 'Si': '71.78', 'K': '0.06', 'Ca': '8.75',
            'Ba': '0.00', 'Fe': '0.00'
        }
        for col_idx, col_name in enumerate(headers):
            item = QTableWidgetItem(defaults.get(col_name, '0.0'))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.input_table.setItem(0, col_idx, item)

        self.input_table.setStyleSheet("""
            QTableWidget {
                background-color: #24283b;
                color: #c0caf5;
                gridline-color: #2f334d;
                border: 1px solid #2f334d;
                border-radius: 6px;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #2f334d;
                color: #7aa2f7;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #7aa2f7;
                color: #1a1b26;
            }
        """)
        self.input_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.input_table.verticalHeader().setVisible(False)
        self.input_table.setMinimumHeight(60)
        input_layout.addWidget(self.input_table)

        btn_row3 = QHBoxLayout()
        self.btn_predict_new = QPushButton("Предсказать Type")
        self.btn_predict_new.setFixedSize(240, 42)
        self.btn_predict_new.setStyleSheet("""
            QPushButton { background-color: #9ece6a; color: #1a1b26; font-weight: bold; }
            QPushButton:hover { background-color: #b5e68a; }
        """)
        btn_row3.addWidget(self.btn_predict_new)

        self.btn_reset_form = QPushButton("Сбросить значения")
        self.btn_reset_form.setFixedSize(200, 42)
        self.btn_reset_form.setStyleSheet("""
            QPushButton { background-color: #3b4261; color: #c0caf5; }
            QPushButton:hover { background-color: #4a5278; }
        """)
        btn_row3.addWidget(self.btn_reset_form)
        btn_row3.addStretch()
        input_layout.addLayout(btn_row3)

        tab3_layout.addWidget(self.input_box)

                # ===== РЕЗУЛЬТАТ ПРЕДСКАЗАНИЯ (С ПРОКРУТКОЙ) =====
        self.result_box = QGroupBox("Результат предсказания")
        result_box_layout = QVBoxLayout(self.result_box)
        result_box_layout.setContentsMargins(15, 25, 15, 15)

        # Контейнер для содержимого (будет прокручиваться)
        result_content = QWidget()
        result_content_layout = QVBoxLayout(result_content)
        result_content_layout.setContentsMargins(0, 0, 0, 0)
        result_content_layout.setSpacing(12)

        self.result_label = QLabel("Введите значения и нажмите «Предсказать Type»")
        self.result_label.setWordWrap(True)
        self.result_label.setMinimumHeight(80)
        self.result_label.setStyleSheet("""
            QLabel {
                background-color: #1a1b26;
                border: 1px solid #2f334d;
                border-radius: 6px;
                padding: 12px;
                color: #c0caf5;
                font-size: 13px;
            }
        """)
        result_content_layout.addWidget(self.result_label)

        self.metrics_label = QLabel("Оценка уверенности появится после предсказания")
        self.metrics_label.setWordWrap(True)
        self.metrics_label.setMinimumHeight(80)
        self.metrics_label.setStyleSheet("""
            QLabel {
                background-color: #1a1b26;
                border: 1px solid #2f334d;
                border-radius: 6px;
                padding: 12px;
                color: #c0caf5;
                font-size: 13px;
            }
        """)
        result_content_layout.addWidget(self.metrics_label)
        result_content_layout.addStretch()

        # ===== QScrollArea для результата =====
        result_scroll = QScrollArea()
        result_scroll.setWidget(result_content)
        result_scroll.setWidgetResizable(True)
        result_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        result_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        result_scroll.setMinimumHeight(300)  # Минимальная высота видимой области
        result_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #2f334d;
                border-radius: 6px;
                background-color: #1a1b26;
            }
            QScrollBar:vertical {
                background-color: #1a1b26;
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #565f89;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #7aa2f7;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        result_box_layout.addWidget(result_scroll)


        tab3_layout.addWidget(self.result_box, 1)

        self.tabWidget.addTab(self.tab3, "Предсказания")

        self.tabWidget.setCurrentIndex(0)
        self.param_stack.setCurrentIndex(0)