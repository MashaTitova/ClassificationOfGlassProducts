"""Точка входа приложения"""

import os
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(PROJECT_DIR, 'app')
for _d in (PROJECT_DIR, APP_DIR):
    if _d not in sys.path:
        sys.path.insert(0, _d)

from PySide6.QtWidgets import QApplication
from views.main_window import GlassApp


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = GlassApp()  
    window.show()
    sys.exit(app.exec())