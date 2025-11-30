#!/usr/bin/env python3
"""
Universal Video Engine - Главный скрипт запуска
"""

import sys
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from core.engine import VideoEngine

if __name__ == '__main__':
    engine = VideoEngine()
    engine.build()