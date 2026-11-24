"""Логирование действий VK-бота в JSON"""

import json
import os
from datetime import datetime

class BotSessionLogger:
    def __init__(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.logs_dir = os.path.join(project_root, "data", "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.logs_dir, f"bot_session_{ts}.json")
        self.session_start = datetime.now()
        self.history = []

    def _log(self, level: str, message: str, user_id: int = None, extra: dict = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "user_id": user_id,
            "message": message,
        }
        if extra:
            entry["extra"] = extra
        self.history.append(entry)
        self._save()

    def info(self, msg: str, user_id: int = None): self._log("INFO", msg, user_id)
    def warning(self, msg: str, user_id: int = None): self._log("WARNING", msg, user_id)
    def error(self, msg: str, user_id: int = None): self._log("ERROR", msg, user_id)
    
    def command(self, cmd: str, user_id: int = None, params: dict = None):
        self._log("COMMAND", cmd, user_id, params)

    def training(self, user_id: int, model_type: str, params: dict, success: bool):
        self._log("TRAINING", f"Обучение {model_type}", user_id, {
            "model_type": model_type, "params": params, "success": success
        })

    def prediction(self, user_id: int, features: dict, result: dict):
        self._log("PREDICTION", "Предсказание", user_id, {
            "features": features,
            "prediction": result.get("prediction"),
            "confidence": result.get("prediction_evaluation", {}).get("confidence")
        })

    def _save(self):
        data = {
            "app": "GlassBot VK",
            "version": "3.3",
            "session_start": self.session_start.isoformat(),
            "session_end": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.session_start).total_seconds(),
            "total_entries": len(self.history),
            "entries": self.history,
        }
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения лога: {e}")
            
    def latest_log_file(self):
        if not os.path.isdir(self.logs_dir):
            return None
        files = sorted(
            (os.path.join(self.logs_dir, f) for f in os.listdir(self.logs_dir)
             if f.startswith("bot_session") and f.endswith(".json")),
            key=os.path.getmtime,
        )
        return files[-1] if files else None


# Глобальный экземпляр для бота
bot_logger = BotSessionLogger()
