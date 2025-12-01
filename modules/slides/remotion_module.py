"""
Remotion модуль - слайды и UI элементы
Для: титульные карточки, текстовые слайды, UI анимации
"""

import subprocess
from pathlib import Path
from typing import Dict, Any
from core.base_module import BaseModule


class RemotionModule(BaseModule):
    """
    Модуль для создания слайдов через Remotion (React)

    Использование в outline.md:

    ## Intro [00:00-00:30]
    TEXT: "Заголовок"
    MODULE: remotion
    COMPONENT: TitleCard

    Или auto-detect:
    COMPONENT: TitleCard  # автоматически использует RemotionModule
    """

    @property
    def module_type(self) -> str:
        return "remotion"

    def validate(self, scene_data: Dict[str, Any]) -> bool:
        """Проверяет что есть имя компонента"""
        return 'component' in scene_data and scene_data['component']

    def render(self, scene_data: Dict[str, Any]) -> Path:
        """
        Рендерит Remotion компонент

        Args:
            scene_data: {
                'component': 'TitleCard',      # имя компонента
                'duration': 30,                # кадры (30fps)
                'text': 'My Title',            # props для компонента
                ... other props
            }

        Returns:
            Path к видео файлу
        """
        component_name = scene_data['component']
        duration_frames = int(
            scene_data.get('duration', 10.0) * self.get_fps())

        self.log(f"Rendering Remotion component: {component_name}")

        # Output path
        output_file = self.output_dir / f"{component_name}.mp4"

        # Remotion command
        cmd = [
            'npx', 'remotion', 'render',
            'remotion/src/index.ts',
            component_name,
            str(output_file),
            '--frames', str(duration_frames),
            '--codec', 'h264'
        ]

        # Add props as input-props
        props = {k: v for k, v in scene_data.items()
                 if k not in ['component', 'duration', 'module']}

        if props:
            import json
            props_json = json.dumps(props)
            cmd.extend(['--props', props_json])

        self.log(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                cwd='remotion'
            )
            self.log(f"✓ Rendered: {output_file}")
            return output_file

        except subprocess.CalledProcessError as e:
            self.log(f"✗ Remotion error: {e.stderr}")
            raise
        except FileNotFoundError:
            self.log("✗ Remotion not installed! Run: npm install in remotion/")
            raise