#!/usr/bin/env python3
"""
StegoGhost - Стеганографическое приложение
Главный файл запуска
"""

import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь поиска модулей
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    # Устанавливаем переменные окружения для лучшей работы на Windows
    if sys.platform == "win32":
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    
    # Импортируем и запускаем приложение
    from gui import main
    main() 