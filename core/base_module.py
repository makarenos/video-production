"""
Базовый класс для всех модулей видеопродакшна
Каждый модуль наследуется от BaseModule и реализует свой тип контента
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


class BaseModule(ABC):
    """
    Абстрактный базовый класс для модулей

    Каждый модуль отвечает за свой тип контента:
    - ManimModule: математика, графики, анимации
    - RemotionModule: слайды, UI элементы
    - ClipModule: видеоклипы, transitions
    - ImageModule: статичные изображения с эффектами
    - DataVizModule: аналитика, charts, дашборды
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
        self.output_dir = Path(config.get('paths', {}).get('module_output',
                                                           'renders')) / self.module_type
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    @abstractmethod
    def module_type(self) -> str:
        """Тип модуля (manim, remotion, clips, etc)"""
        pass

    @abstractmethod
    def render(self, scene_data: Dict[str, Any]) -> Path:
        """
        Рендерит сцену и возвращает путь к видео файлу

        Args:
            scene_data: Данные сцены из outline

        Returns:
            Path к сгенерированному видео файлу
        """
        pass

    @abstractmethod
    def validate(self, scene_data: Dict[str, Any]) -> bool:
        """
        Проверяет что модуль может обработать эти данные

        Args:
            scene_data: Данные сцены

        Returns:
            True если модуль может обработать
        """
        pass

    def get_duration(self, scene_data: Dict[str, Any]) -> float:
        """Возвращает длительность сцены в секундах"""
        return scene_data.get('duration', 10.0)

    def get_resolution(self) -> tuple:
        """Возвращает разрешение из конфига"""
        return tuple(self.config['project']['resolution'])

    def get_fps(self) -> int:
        """Возвращает FPS из конфига"""
        return self.config['project']['fps']

    def log(self, message: str):
        """Логирование"""
        print(f"[{self.name}] {message}")


class ModuleRegistry:
    """
    Реестр всех доступных модулей
    Автоматически определяет какой модуль использовать для сцены
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.modules: Dict[str, BaseModule] = {}

    def register(self, module_class: type):
        """Регистрирует новый модуль"""
        module = module_class(self.config)
        self.modules[module.module_type] = module
        print(f"✓ Зарегистрирован модуль: {module.module_type}")

    def get_module(self, scene_data: Dict[str, Any]) -> Optional[BaseModule]:
        """
        Возвращает подходящий модуль для сцены

        Определяет по полям:
        - module: explicit module type
        - scene: manim scene name
        - component: remotion component
        - clip: video clip
        - image: static image
        - chart: data visualization
        """
        # Explicit module type
        if 'module' in scene_data:
            return self.modules.get(scene_data['module'])

        # Auto-detect by fields
        if 'scene' in scene_data:
            return self.modules.get('manim')
        if 'component' in scene_data:
            return self.modules.get('remotion')
        if 'clip' in scene_data:
            return self.modules.get('clips')
        if 'image' in scene_data:
            return self.modules.get('images')
        if 'chart' in scene_data or 'data' in scene_data:
            return self.modules.get('dataviz')

        # Default fallback
        return self.modules.get('slides')

    def list_modules(self):
        """Список всех доступных модулей"""
        return list(self.modules.keys())