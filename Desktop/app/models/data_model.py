"""Модель данных: загрузка, очистка, разбиение"""

import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from dataclasses import dataclass
from typing import Optional


#Файл по умолчанию
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_APP_DIR = os.path.join(_PROJECT_ROOT, 'app')
for _d in (_PROJECT_ROOT, _APP_DIR):
    if _d not in sys.path:
        sys.path.insert(0, _d)


FEATURE_COLUMNS = ['RI', 'Na', 'Mg', 'Al', 'Si', 'K', 'Ca', 'Ba', 'Fe']
TARGET_COLUMN = 'Type'
DEFAULT_DATA_FILE = 'glassData.txt'


@dataclass
class Dataset:
    raw: pd.DataFrame
    X: pd.DataFrame
    y: pd.Series
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    source_path: str


class DataModel:
    """Работа с датасетом стекла."""

    def __init__(self):
        self._dataset: Optional[Dataset] = None

    @property
    def dataset(self) -> Optional[Dataset]:
        return self._dataset

    @property
    def project_root(self) -> str:
        """Корень проекта — вычисляется автоматически"""
        return _PROJECT_ROOT

    @property
    def default_data_path(self) -> str:
        """Путь к файлу данных по умолчанию"""
        return os.path.join(_PROJECT_ROOT, DEFAULT_DATA_FILE)

    def load(self, path: str) -> Dataset:
        """Загружает данные по полному пути"""
        df = pd.read_csv(path, sep=",")
        if "Id" in df.columns:
            df = df.drop(columns=["Id"])

        X = df.drop(TARGET_COLUMN, axis=1)
        y = df[TARGET_COLUMN]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        self._dataset = Dataset(
            raw=df, X=X, y=y,
            X_train=X_train, X_test=X_test,
            y_train=y_train, y_test=y_test,
            source_path=path
        )
        return self._dataset

    def load_default(self) -> Dataset:
        """Загружает glassData.txt из корня проекта"""
        path = self.default_data_path
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Файл данных не найден: {path}\n"
                f"Убедитесь, что '{DEFAULT_DATA_FILE}' лежит в корне проекта: {_PROJECT_ROOT}"
            )
        return self.load(path)