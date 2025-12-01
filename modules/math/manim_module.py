"""
Manim модуль - математические анимации и графики
Для: формулы, графики, диаграммы, математические визуализации
"""

import subprocess
from pathlib import Path
from typing import Dict, Any
from core.base_module import BaseModule


class ManimModule(BaseModule):
    """
    Модуль для создания математических анимаций через Manim

    Использование в outline.md:

    ## Scene Title [00:00-00:30]
    TEXT: "Смотрите на формулу"
    MODULE: manim
    SCENE: InflationFormula

    Или auto-detect:
    SCENE: InflationFormula  # автоматически использует ManimModule
    """

    @property
    def module_type(self) -> str:
        return "manim"

    def validate(self, scene_data: Dict[str, Any]) -> bool:
        """Проверяет что есть имя сцены"""
        return 'scene' in scene_data and scene_data['scene']

    def render(self, scene_data: Dict[str, Any]) -> Path:
        """
        Рендерит Manim сцену

        Args:
            scene_data: {
                'scene': 'InflationFormula',  # имя класса в manim/manim_module.py
                'duration': 10.0,              # длительность (опционально)
                'quality': 'high',             # low, medium, high (опционально)
            }

        Returns:
            Path к видео файлу
        """
        scene_name = scene_data['scene']
        quality = scene_data.get('quality',
                                 self.config['render'].get('quality',
                                                           'medium'))

        self.log(f"Rendering Manim scene: {scene_name}")

        # Quality flags
        quality_flags = {
            'low': '-ql',
            'medium': '-qm',
            'high': '-qh',
            'ultra': '-qk'
        }
        quality_flag = quality_flags.get(quality, '-qm')

        # Output path
        output_file = self.output_dir / f"{scene_name}.mp4"

        # Manim command
        cmd = [
            'manim',
            quality_flag,
            '--format', 'mp4',
            '-o', str(output_file),
            'manim/manim_module.py',
            scene_name
        ]

        self.log(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            self.log(f"✓ Rendered: {output_file}")
            return output_file

        except subprocess.CalledProcessError as e:
            self.log(f"✗ Manim error: {e.stderr}")
            raise
        except FileNotFoundError:
            self.log("✗ Manim not installed! Run: pip install manim")
            raise

    def get_available_scenes(self) -> list:
        """Возвращает список доступных Manim сцен"""
        scenes_file = Path('manim/manim_module.py')
        if not scenes_file.exists():
            return []

        # Simple regex to find class definitions
        import re
        content = scenes_file.read_text()
        pattern = r'class\s+(\w+)\s*\(.*Scene\)'
        scenes = re.findall(pattern, content)

        return scenes