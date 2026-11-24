"""OLAP-модель: многомерный анализ датасета
"""

from dataclasses import dataclass
from typing import Optional, List
import pandas as pd

BIN_COUNT = 4  # число интервалов при разбиении числового признака

AGG_FUNCS = {
    'Количество': 'count',
    'Среднее': 'mean',
    'Минимум': 'min',
    'Максимум': 'max',
    'Сумма': 'sum',
}

MEASURE_ALL = 'Количество объектов'


@dataclass
class Cube:
    """Результат OLAP-среза"""
    row_dim: str
    col_dim: str
    measure: str
    agg: str
    table: pd.DataFrame  # сводная таблица с итогами


class OLAPModel:
    """Строит OLAP-куб поверх загруженного датасета."""

    def __init__(self):
        self._df: Optional[pd.DataFrame] = None
        self._cube: Optional[Cube] = None

    @property
    def cube(self) -> Optional[Cube]:
        return self._cube

    @property
    def has_data(self) -> bool:
        return self._df is not None and not self._df.empty

    @property
    def df(self) -> Optional[pd.DataFrame]:
        return self._df

    def set_data(self, df: pd.DataFrame):
        self._df = df.copy()

    def _numeric_columns(self) -> List[str]:
        """Числовые колонки файла"""
        if self._df is None:
            return []
        excluded = {'Id', 'Type', 'index', 'Unnamed: 0'}
        return [
            c for c in self._df.columns
            if c not in excluded and pd.api.types.is_numeric_dtype(self._df[c])
        ]

    def _label_column(self) -> Optional[str]:
        """Целевая колонка: 'Type', если есть, иначе первая нечисловая"""
        if self._df is None:
            return None
        if 'Type' in self._df.columns:
            return 'Type'
        for c in self._df.columns:
            if c not in {'Id', 'Unnamed: 0'} and not pd.api.types.is_numeric_dtype(self._df[c]):
                return c
        return None

    def dimensions(self) -> List[str]:
        """Доступные измерения: целевая колонка + числовые признаки файла"""
        label = self._label_column()
        dims = [label] if label else []
        return dims + self._numeric_columns()

    def measures(self) -> List[str]:
        """Доступные меры: количество объектов + числовые признаки файла"""
        return [MEASURE_ALL] + self._numeric_columns()

    def _make_dim(self, series: pd.Series, name: str) -> pd.Series:
        """Превращает колонку в измерение:
        нечисловая — значения как есть, числовая — квантильные интервалы"""
        if not pd.api.types.is_numeric_dtype(series):
            return series.astype(str)
        try:
            _, edges = pd.qcut(series, q=BIN_COUNT, retbins=True, duplicates='drop')
            labels = [f'{name} [{edges[i]:.2f}–{edges[i+1]:.2f}]' for i in range(len(edges) - 1)]
            return pd.cut(series, bins=edges, labels=labels, include_lowest=True).astype(str)
        except Exception:
            return series.map(lambda v: f'{name} {v}')

    def build(self, row_dim: str, col_dim: str, measure: str, agg_name: str) -> Cube:
        """Строит сводную таблицу (срез куба) с итогами по строкам и столбцам"""
        if self._df is None:
            raise RuntimeError('Данные не загружены')
        if row_dim not in self._df.columns or col_dim not in self._df.columns:
            raise ValueError('Измерение отсутствует в заголовках файла')
        if row_dim == col_dim:
            raise ValueError('Строки и столбцы должны быть разными измерениями')
        if measure != MEASURE_ALL and measure not in self._df.columns:
            raise ValueError(f'Мера "{measure}" отсутствует в заголовках файла')

        df = self._df.copy()
        df['_row'] = self._make_dim(df[row_dim], row_dim)
        df['_col'] = self._make_dim(df[col_dim], col_dim)

        common = dict(index='_row', columns='_col', margins=True, margins_name='Итого')

        if measure == MEASURE_ALL:
            table = pd.pivot_table(df, values=row_dim, aggfunc='size', fill_value=0, **common)
        elif AGG_FUNCS.get(agg_name) == 'count':
            table = pd.pivot_table(df, values=measure, aggfunc='count', fill_value=0, **common)
        else:
            table = pd.pivot_table(
                df, values=measure, aggfunc=AGG_FUNCS.get(agg_name, 'mean'), **common
            )

        table = table.round(3)
        self._cube = Cube(row_dim=row_dim, col_dim=col_dim,
                          measure=measure, agg=agg_name, table=table)
        return self._cube

    def get_detail(self, row_dim: str, row_value: str,
                   col_dim: str = None, col_value: str = None) -> pd.DataFrame:
        """Drill-down: исходные записи, попавшие в выбранную ячейку"""
        if self._df is None:
            raise RuntimeError('Данные не загружены')
        df = self._df.copy()
        mask = self._make_dim(df[row_dim], row_dim).astype(str) == str(row_value)
        if col_value is not None:
            mask &= self._make_dim(df[col_dim], col_dim).astype(str) == str(col_value)
        return df.loc[mask]
