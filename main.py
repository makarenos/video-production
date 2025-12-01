#!/usr/bin/env python3
"""
Universal Video Engine - Главный скрипт запуска
Модульная система для создания любых типов видео
"""

import sys
import argparse
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from core.engine import VideoEngine
from rich.console import Console

console = Console()


def main():
    parser = argparse.ArgumentParser(
        description='Universal Video Production Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Собрать видео из outline.md
  python main.py

  # Использовать другой outline
  python main.py --outline my_video.md

  # Указать output путь
  python main.py --output output/my_video.mp4

  # Список доступных модулей
  python main.py --list-modules
        """
    )

    parser.add_argument(
        '--outline', '-o',
        default='outline.md',
        help='Path to outline.md file (default: outline.md)'
    )

    parser.add_argument(
        '--output',
        help='Output video path (default: output/<project_name>.mp4)'
    )

    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to config.yaml (default: config.yaml)'
    )

    parser.add_argument(
        '--list-modules', '-l',
        action='store_true',
        help='List all available modules'
    )

    args = parser.parse_args()

    try:
        engine = VideoEngine(config_path=args.config)

        if args.list_modules:
            engine.list_modules()
            return

        engine.build(
            outline_path=args.outline,
            output_path=args.output
        )

    except FileNotFoundError as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        console.print(
            "\n[yellow]Tip: Make sure config.yaml and outline.md exist[/yellow]")
        sys.exit(1)

    except Exception as e:
        console.print(f"[red]✗ Unexpected error: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()