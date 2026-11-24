# -*- coding: utf-8 -*-
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
        try:
            self.log_added.emit(ts, level.value, message)
        except Exception:
            pass

    def info(self, msg: str):    self._emit(LogLevel.INFO, msg)
    def success(self, msg: str): self._emit(LogLevel.SUCCESS, msg)
    def warning(self, msg: str): self._emit(LogLevel.WARNING, msg)
    def error(self, msg: str):   self._emit(LogLevel.ERROR, msg)

    def clear(self):
        self._history.clear()

    @property
    def history(self):
        return list(self._history)

    def save_to_json(self, base_dir: str = None) -> str:
        if base_dir is None:
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logs_dir = Path(base_dir) / "data" / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        session_end = datetime.now()
        filename = f"session_{session_end.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = logs_dir / filename
        data = {
            "app": "GlassBot",
            "version": "3.4",
            "session_start": self._session_start.isoformat(),
            "session_end": session_end.isoformat(),
            "duration_seconds": (session_end - self._session_start).total_seconds(),
            "total_entries": len(self._history),
            "entries": [
                {"timestamp": ts, "level": level, "message": message}
                for ts, level, message in self._history
            ]
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return str(filepath)