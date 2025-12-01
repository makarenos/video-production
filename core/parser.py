"""
Парсер outline.md файла
Преобразует markdown сценарий в структурированные данные для модулей
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Scene:
    """Сцена видео"""
    title: str
    timestamp: str
    start_time: float
    end_time: float
    duration: float
    text: str = ""
    module: str = None

    # Module-specific parameters
    scene: str = None  # Manim scene name
    component: str = None  # Remotion component
    clip: str = None  # Video clip path
    image: str = None  # Image path
    chart: str = None  # Chart type
    data: str = None  # Data source

    # Additional parameters
    params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate duration if not set"""
        if self.duration == 0:
            self.duration = self.end_time - self.start_time


class OutlineParser:
    """
    Парсер outline.md

    Формат:

    ## Scene Title [00:00-00:30]
    TEXT: "Voice-over text"
    MODULE: manim
    SCENE: InflationChart

    ## Another Scene [00:30-01:00]
    TEXT: "More text"
    COMPONENT: OpinionSlide
    PARAM: background: "#1a1a1a"
    """

    def __init__(self, outline_path: str):
        self.outline_path = Path(outline_path)
        self.scenes: List[Scene] = []

    def parse(self) -> List[Scene]:
        """Парсит outline и возвращает список сцен"""
        if not self.outline_path.exists():
            raise FileNotFoundError(
                f"Outline file not found: {self.outline_path}")

        content = self.outline_path.read_text(encoding='utf-8')

        # Split by ## headers
        sections = re.split(r'\n## ', content)

        for section in sections[1:]:  # Skip document title
            scene = self._parse_section(section)
            if scene:
                self.scenes.append(scene)

        return self.scenes

    def _parse_section(self, section: str) -> Scene:
        """Parse one section into Scene"""
        lines = section.strip().split('\n')
        if not lines:
            return None

        # Parse header: "Title [MM:SS-MM:SS]"
        header = lines[0]
        match = re.match(r'(.+?)\s*\[(.+?)\]', header)

        if not match:
            return None

        title = match.group(1).strip()
        timestamp = match.group(2).strip()

        # Parse timestamps
        start_time, end_time = self._parse_timestamp(timestamp)
        duration = end_time - start_time

        # Parse parameters
        params = self._parse_params(lines[1:])

        # Extract known fields
        scene = Scene(
            title=title,
            timestamp=timestamp,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            text=params.pop('TEXT', ''),
            module=params.pop('MODULE', None),
            scene=params.pop('SCENE', None),
            component=params.pop('COMPONENT', None),
            clip=params.pop('CLIP', None),
            image=params.pop('IMAGE', None),
            chart=params.pop('CHART', None),
            data=params.pop('DATA', None),
            params=params  # Remaining parameters
        )

        return scene

    def _parse_timestamp(self, timestamp: str) -> tuple:
        """Parse 'MM:SS-MM:SS' or 'SS-SS' into (start, end) seconds"""
        parts = timestamp.split('-')
        if len(parts) != 2:
            raise ValueError(f"Invalid timestamp format: {timestamp}")

        start = self._time_to_seconds(parts[0].strip())
        end = self._time_to_seconds(parts[1].strip())

        return start, end

    def _time_to_seconds(self, time_str: str) -> float:
        """Convert 'MM:SS' or 'SS' to seconds"""
        parts = time_str.split(':')

        if len(parts) == 1:
            return float(parts[0])
        elif len(parts) == 2:
            minutes, seconds = map(float, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:
            hours, minutes, seconds = map(float, parts)
            return hours * 3600 + minutes * 60 + seconds
        else:
            raise ValueError(f"Invalid time format: {time_str}")

    def _parse_params(self, lines: List[str]) -> Dict[str, Any]:
        """Parse parameter lines into dict"""
        params = {}

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")

                # Try to convert to number
                try:
                    value = float(value)
                    if value.is_integer():
                        value = int(value)
                except ValueError:
                    pass

                params[key] = value

        return params

    def get_total_duration(self) -> float:
        """Get total video duration"""
        if not self.scenes:
            return 0.0
        return max(scene.end_time for scene in self.scenes)

    def validate(self) -> bool:
        """Validate parsed scenes"""
        if not self.scenes:
            print("⚠️  No scenes found in outline")
            return False

        # Check for overlaps
        for i, scene in enumerate(self.scenes[:-1]):
            next_scene = self.scenes[i + 1]
            if scene.end_time > next_scene.start_time:
                print(
                    f"⚠️  Scene overlap: {scene.title} ends at {scene.end_time}s but {next_scene.title} starts at {next_scene.start_time}s")

        return True