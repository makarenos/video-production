"""
Image модуль - статичные изображения с эффектами
Для: показ изображений, фотографий, скриншотов с эффектами (zoom, pan, Ken Burns)
"""

from pathlib import Path
from typing import Dict, Any
from core.base_module import BaseModule


class ImageModule(BaseModule):
    """
    Модуль для работы с изображениями

    Использование в outline.md:

    ## Image [00:30-01:00]
    TEXT: "Вот график"
    MODULE: images
    IMAGE: assets/images/chart.png
    EFFECT: zoom_in

    Или auto-detect:
    IMAGE: path/to/image.png  # автоматически использует ImageModule
    """

    @property
    def module_type(self) -> str:
        return "images"

    def validate(self, scene_data: Dict[str, Any]) -> bool:
        """Проверяет что есть путь к изображению"""
        return 'image' in scene_data and scene_data['image']

    def render(self, scene_data: Dict[str, Any]) -> Path:
        """
        Создает видео из изображения с эффектами

        Args:
            scene_data: {
                'image': 'assets/images/chart.png',
                'duration': 5.0,
                'effect': 'zoom_in',  # zoom_in, zoom_out, pan_right, ken_burns, static
            }

        Returns:
            Path к видео файлу
        """
        image_path = Path(scene_data['image'])
        duration = scene_data.get('duration', 5.0)
        effect = scene_data.get('effect', 'static')

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        self.log(f"Creating video from image: {image_path.name}")

        # Output path
        output_file = self.output_dir / f"{image_path.stem}_{effect}.mp4"

        # Use MoviePy to create video from image
        try:
            from moviepy.editor import ImageClip, CompositeVideoClip
            import numpy as np

            # Load image
            clip = ImageClip(str(image_path), duration=duration)

            # Apply effect
            if effect == 'zoom_in':
                clip = self._apply_zoom_in(clip, duration)
            elif effect == 'zoom_out':
                clip = self._apply_zoom_out(clip, duration)
            elif effect == 'pan_right':
                clip = self._apply_pan_right(clip, duration)
            elif effect == 'ken_burns':
                clip = self._apply_ken_burns(clip, duration)
            # 'static' = no effect

            # Set resolution
            clip = clip.resize(self.get_resolution())

            # Render
            clip.write_videofile(
                str(output_file),
                fps=self.get_fps(),
                codec=self.config['render']['codec'],
                preset=self.config['render']['preset'],
                audio=False,
                verbose=False,
                logger=None
            )

            clip.close()

            self.log(f"✓ Created: {output_file}")
            return output_file

        except ImportError:
            self.log("✗ MoviePy not installed! Run: pip install moviepy")
            raise

    def _apply_zoom_in(self, clip, duration):
        """Zoom in effect (1.0 → 1.2x scale)"""
        from moviepy.video.fx import resize

        def zoom(t):
            zoom_factor = 1.0 + 0.2 * (t / duration)
            return clip.resize(zoom_factor)

        return clip.fl(lambda gf, t: zoom(t).get_frame(t))

    def _apply_zoom_out(self, clip, duration):
        """Zoom out effect (1.2 → 1.0x scale)"""
        from moviepy.video.fx import resize

        def zoom(t):
            zoom_factor = 1.2 - 0.2 * (t / duration)
            return clip.resize(zoom_factor)

        return clip.fl(lambda gf, t: zoom(t).get_frame(t))

    def _apply_pan_right(self, clip, duration):
        """Pan right effect"""
        # Increase clip width and pan across
        clip = clip.resize(width=int(self.get_resolution()[0] * 1.3))

        def pan(t):
            x_offset = int(
                (clip.w - self.get_resolution()[0]) * (t / duration))
            return clip.crop(x1=x_offset, width=self.get_resolution()[0])

        return clip.fl(lambda gf, t: pan(t).get_frame(t))

    def _apply_ken_burns(self, clip, duration):
        """Ken Burns effect (zoom + pan)"""
        # Combine zoom and pan
        clip = clip.resize(width=int(self.get_resolution()[0] * 1.5))

        def ken_burns(t):
            progress = t / duration
            zoom_factor = 1.0 + 0.3 * progress
            x_offset = int((clip.w - self.get_resolution()[0]) * progress)

            zoomed = clip.resize(zoom_factor)
            return zoomed.crop(x1=x_offset, width=self.get_resolution()[0])

        return clip.fl(lambda gf, t: ken_burns(t).get_frame(t))