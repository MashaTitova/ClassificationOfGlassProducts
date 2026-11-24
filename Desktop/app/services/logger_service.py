"""Сервис логирования действий пользователя"""

import os
import json
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QDateTime
from enum import Enum


class LogLevel(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class LoggerService(QObject):
    log_added = Signal(str, str, str)  

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True
        self._history = []
        self._max_history = 500
        self._session_start = datetime.now()

    def _emit(self, level: LogLevel, message: str):
        ts = QDateTime.currentDateTime().toString("HH:mm:ss")
        self._history.append((ts, level.value, message))
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        self.log_added.emit(ts, level.value, message)

    def info(self, msg: str):    self._emit(LogLevel.INFO, msg)
    def success(self, msg: str): self._emit(LogLevel.SUCCESS, msg)
    def warning(self, msg: str): self._emit(LogLevel.WARNING, msg)
    def error(self, msg: str):   self._emit(LogLevel.ERROR, msg)

    def clear(self):
        self._history.clear()

    @property
    def history(self):
        return list(self._history)

    #Сохранение в JSON
    def save_to_json(self, base_dir: str = None) -> str:
        """
        Сохраняет всю историю логов в JSON-файл.
        Возвращает путь к сохранённому файлу.
        """
        if base_dir is None:
            # По умолчанию — папка logs/ в корне проекта
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )

        logs_dir = Path(base_dir) / "logs"
        logs_dir.mkdir(exist_ok=True)

        session_end = datetime.now()
        filename = f"session_{session_end.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = logs_dir / filename

        data = {
            "app": "Classification of Glass Products",
            "version": "3.4",
            "session_start": self._session_start.isoformat(),
            "session_end": session_end.isoformat(),
            "duration_seconds": (session_end - self._session_start).total_seconds(),
            "total_entries": len(self._history),
            "entries": [
                {
                    "timestamp": ts,
                    "level": level,
                    "message": message
                }
                for ts, level, message in self._history
            ]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def append_to_json(self, base_dir: str = None) -> str:
        """
        Дописывает новые записи в текущий сессионный JSON.
        """
        if base_dir is None:
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )

        logs_dir = Path(base_dir) / "logs"
        logs_dir.mkdir(exist_ok=True)

        today = datetime.now().strftime('%Y%m%d')
        existing = list(logs_dir.glob(f"session_{today}_*.json"))

        if existing:
            filepath = sorted(existing)[-1]  
        else:
            filepath = logs_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                "app": "Classification of Glass Products",
                "version": "3.3",
                "session_start": self._session_start.isoformat(),
                "session_end": None,
                "duration_seconds": None,
                "total_entries": 0,
                "entries": []
            }

        # Добавляем только новые записи
        current_count = data.get("total_entries", 0)
        new_entries = self._history[current_count:]

        for ts, level, message in new_entries:
            data["entries"].append({
                "timestamp": ts,
                "level": level,
                "message": message
            })

        data["total_entries"] = len(data["entries"])
        data["session_end"] = datetime.now().isoformat()
        data["duration_seconds"] = (
            datetime.now() - self._session_start
        ).total_seconds()

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return str(filepath)