# -*- coding: utf-8 -*-
"""ViewModel вкладки OLAP-анализа"""

from PySide6.QtCore import QObject, Signal

from models.olap_model import OLAPModel
from models.data_model import Dataset
from services.logger_service import LoggerService


class OlapViewModel(QObject):
    dimensions_ready = Signal(list, list)   # (измерения, меры)
    cube_ready = Signal(object)             # Cube
    detail_ready = Signal(object, str)      # (DataFrame, описание фильтра)
    message = Signal(str, str)

    def __init__(self, olap_model: OLAPModel, logger: LoggerService):
        super().__init__()
        self.olap_model = olap_model
        self.logger = logger

    def set_dataset(self, dataset: Dataset):
        self.olap_model.set_data(dataset.raw)
        self.logger.info(f'OLAP: данные установлены ({len(dataset.raw)} записей)')
        self.dimensions_ready.emit(
            self.olap_model.dimensions(), self.olap_model.measures()
        )

    def build(self, row_dim: str, col_dim: str, measure: str, agg_name: str):
        self.logger.info(f'OLAP: срез {row_dim} × {col_dim} | {measure} ({agg_name})')
        try:
            cube = self.olap_model.build(row_dim, col_dim, measure, agg_name)
            cells = (cube.table.shape[0] - 1) * (cube.table.shape[1] - 1)
            self.logger.success(f'OLAP: куб построен, ячеек данных: {cells}')
            self.cube_ready.emit(cube)
        except Exception as e:
            self.logger.error(f'OLAP: ошибка построения куба: {e}')
            self.message.emit('error', str(e))

    def request_detail(self, row_dim, row_value, col_dim, col_value):
        desc = f'{row_dim} = {row_value}' + (f' × {col_dim} = {col_value}' if col_value else '')
        try:
            df = self.olap_model.get_detail(row_dim, row_value, col_dim, col_value)
            self.detail_ready.emit(df, desc)
            self.logger.info(f'OLAP: детализация [{desc}] — {len(df)} объектов')
        except Exception as e:
            self.logger.error(f'OLAP: ошибка детализации: {e}')
            self.message.emit('error', str(e))
