#!/usr/bin/env python3
"""
Главный скрипт для автоматизации видеопродакшна
Парсит outline.md и собирает финальное видео
"""

import yaml
import re
import os
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Segment:
    """Сегмент видео"""
    title: str
    timestamp: str
    text: str
    seg_type: str
    visual: str
    scene: str = None
    component: str = None
    duration: float = 10.0


class OutlineParser:
    """Парсер outline.md файла"""
    
    def __init__(self, outline_path: str):
        self.outline_path = outline_path
        self.segments: List[Segment] = []
    
    def parse(self) -> List[Segment]:
        """Парсит outline и возвращает список сегментов"""
        with open(self.outline_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Разбиваем на секции по заголовкам ##
        sections = re.split(r'\n## ', content)
        
        for section in sections[1:]:  # Пропускаем первый элемент (заголовок документа)
            segment = self._parse_section(section)
            if segment:
                self.segments.append(segment)
        
        return self.segments
    
    def _parse_section(self, section: str) -> Segment:
        """Парсит одну секцию outline"""
        lines = section.strip().split('\n')
        
        # Первая строка - заголовок с timestamp
        header = lines[0]
        match = re.match(r'(.+?)\s*\[(.+?)\]', header)
        
        if not match:
            return None
        
        title = match.group(1).strip()
        timestamp = match.group(2).strip()
        
        # Парсим временные метки
        start, end = timestamp.split('-')
        duration = self._parse_time(end) - self._parse_time(start)
        
        # Парсим параметры
        params = {}
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                params[key.strip()] = value.strip().strip('"')
        
        return Segment(
            title=title,
            timestamp=timestamp,
            text=params.get('TEXT', ''),
            seg_type=params.get('TYPE', 'title'),
            visual=params.get('VISUAL', ''),
            scene=params.get('SCENE', None),
            component=params.get('COMPONENT', None),
            duration=duration
        )
    
    def _parse_time(self, time_str: str) -> float:
        """Конвертирует время из формата MM:SS в секунды"""
        parts = time_str.split(':')
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        return float(parts[0])


class VideoBuilder:
    """Сборщик финального видео"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.project_root = Path(__file__).parent.parent
    
    def build(self, segments: List[Segment], output_path: str = None):
        """Собирает финальное видео из сегментов"""
        
        if output_path is None:
            output_path = self.project_root / self.config['paths']['final_output'] / 'final.mp4'
        
        print(f"\n{'='*60}")
        print(f"  Сборка видео: {self.config['project']['name']}")
        print(f"{'='*60}\n")
        
        print(f"📋 Всего сегментов: {len(segments)}\n")
        
        for i, seg in enumerate(segments, 1):
            print(f"  {i}. {seg.title} [{seg.timestamp}]")
            print(f"     Тип: {seg.seg_type} | Длительность: {seg.duration}s")
            if seg.scene:
                print(f"     Manim сцена: {seg.scene}")
            if seg.component:
                print(f"     Remotion компонент: {seg.component}")
            print()
        
        print(f"\n{'='*60}")
        print(f"  ✓ План сборки готов!")
        print(f"{'='*60}\n")
        
        return segments


def main():
    """Главная функция"""
    
    # Парсим outline
    parser = OutlineParser('outline.md')
    segments = parser.parse()
    
    # Строим видео
    builder = VideoBuilder()
    builder.build(segments)
    
    print("✓ Тестовый прогон завершен успешно!\n")
    print("Следующие шаги:")
    print("  1. Проверить установку Manim")
    print("  2. Создать Remotion проект")
    print("  3. Добавить рендеринг сегментов")
    print("  4. Интегрировать MoviePy для финальной сборки\n")


if __name__ == '__main__':
    main()
