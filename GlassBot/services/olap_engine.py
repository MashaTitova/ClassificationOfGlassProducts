# -*- coding: utf-8 -*-
"""Движок OLAP-куба: многомерная агрегация + тепловая карта.
Работает с любым датасетом: названия колонок определяются на лету."""

import numpy as np
import pandas as pd
from matplotlib.figure import Figure


class OLEngine:
    AGGREGATIONS = ['mean', 'median', 'std', 'sum', 'min', 'max']

    @staticmethod
    def _numeric_cols(df: pd.DataFrame) -> list:
        return [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

    @staticmethod
    def _binned(df: pd.DataFrame, col: str, bins: int = 5) -> pd.Series:
        return pd.cut(df[col], bins=bins)

    @staticmethod
    def _find_target(df: pd.DataFrame) -> str:
        """Целевая колонка: известные имена, иначе последняя колонка."""
        aliases = {"type", "target", "class", "label", "y"}
        for c in df.columns:
            if str(c).lower() in aliases:
                return c
        return df.columns[-1]

    @classmethod
    def _resolve_row_dim(cls, df: pd.DataFrame, row_dim: str) -> pd.Series:
        """Размер группировки: готовая колонка, бинированный признак или цель."""
        if row_dim in df.columns:
            return df[row_dim]

        suffix = " (bins)"
        if row_dim.endswith(suffix):
            base = row_dim[: -len(suffix)]  
            if base in df.columns:
                return cls._binned(df, base)

        # запасной вариант: цель датасета
        target = cls._find_target(df)
        if target in df.columns:
            return df[target]

        raise ValueError(
            f"Не удалось построить группировку по '{row_dim}'. "
            f"Доступные колонки: {', '.join(map(str, df.columns))}"
        )

    @classmethod
    def _resolve_measure(cls, df: pd.DataFrame, measure: str):
        """Возвращает (серия значений меры, aggfunc). Count -> единицы."""
        if measure == "Count" or measure not in df.columns:
            return pd.Series(1, index=df.index), "sum"
        return df[measure], None  

    @classmethod
    def build_cube(cls, df: pd.DataFrame, measure: str, row_dim: str,
                   aggfunc: str = 'mean') -> pd.DataFrame:
        """
        Возвращает pivot-таблицу — ядро OLAP-куба.
        measure:  что агрегируем (любая числовая колонка или 'Count')
        row_dim:  по чему группируем (цель, любая колонка или 'Признак (bins)')
        aggfunc:  функция агрегации
        """
        work = df.copy()

        # Размер группировки — динамически
        work["_row"] = cls._resolve_row_dim(work, row_dim)

        # Мера — динамически; для Count агрегация всегда sum
        values, forced_agg = cls._resolve_measure(work, measure)
        work["_measure"] = values
        if forced_agg:
            aggfunc = forced_agg

        pivot = work.pivot_table(index="_row", values="_measure",
                                 aggfunc=aggfunc, observed=True)
        return pivot

    @classmethod
    def render_heatmap(cls, pivot: pd.DataFrame, measure: str,
                       row_dim: str, aggfunc: str) -> Figure:
        """Рисует тепловую карту куба в тёмной теме."""
        fig = Figure(figsize=(9, 6), dpi=100)
        fig.patch.set_facecolor('#1a1b26')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1a1b26')

        data = pivot.values.astype(float)
        rows = [str(r) for r in pivot.index]

        if data.shape[1] == 1:
            vals = data.ravel()
            colors = ['#7aa2f7', '#bb9af7', '#7dcfff', '#9ece6a',
                      '#f7768e', '#e0af68', '#ff9e64']
            ax.barh(rows, vals, color=colors[:len(rows)])
            ax.set_title(f'OLAP-куб: {aggfunc}({measure}) по {row_dim}',
                         color='white', fontsize=13)
            ax.set_xlabel(aggfunc, color='white')
            ax.tick_params(colors='white')
            for lbl in ax.get_yticklabels():
                lbl.set_color('white')
            ax.grid(axis='x', alpha=0.3, color='gray')
        else:
            im = ax.imshow(data, cmap='viridis', aspect='auto')
            ax.set_xticks(range(data.shape[1]))
            ax.set_xticklabels([str(c) for c in pivot.columns], color='white')
            ax.set_yticks(range(len(rows)))
            ax.set_yticklabels(rows, color='white')
            ax.set_title(f'OLAP-куб: {aggfunc}({measure}) по {row_dim}',
                         color='white', fontsize=13)
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    if not np.isnan(data[i, j]):
                        ax.text(j, i, f'{data[i, j]:.2f}', ha='center',
                                va='center', color='white', fontsize=8)
            cbar = fig.colorbar(im, ax=ax)
            cbar.ax.yaxis.set_tick_params(color='white')
            for lbl in cbar.ax.yaxis.get_ticklabels():
                lbl.set_color('white')

        fig.tight_layout()
        return fig
