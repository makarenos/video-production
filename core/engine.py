"""
Главный движок видеопродакшна
Координирует работу всех модулей и собирает финальное видео
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from core.parser import OutlineParser, Scene
from core.base_module import ModuleRegistry


class VideoEngine:
    """
    Главный движок видеопродакшна

    Workflow:
    1. Парсит outline.md
    2. Определяет какой модуль нужен для каждой сцены
    3. Рендерит каждую сцену через соответствующий модуль
    4. Собирает финальное видео через MoviePy
    """

    def __init__(self, config_path: str = 'config.yaml'):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.console = Console()

        # Initialize registry
        self.registry = ModuleRegistry(self.config)

        # Register all available modules
        self._register_modules()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _register_modules(self):
        """Register all available modules"""
        # Import modules here to avoid circular imports
        try:
            from modules.math.manim_module import ManimModule
            self.registry.register(ManimModule)
        except ImportError as e:
            self.console.print(
                f"[yellow]⚠️  ManimModule not available: {e}[/yellow]")

        try:
            from modules.slides.remotion_module import RemotionModule
            self.registry.register(RemotionModule)
        except ImportError as e:
            self.console.print(
                f"[yellow]⚠️  RemotionModule not available: {e}[/yellow]")

        try:
            from modules.images.image_module import ImageModule
            self.registry.register(ImageModule)
        except ImportError as e:
            self.console.print(
                f"[yellow]⚠️  ImageModule not available: {e}[/yellow]")

        # Add more modules as they're created

    def build(self, outline_path: str = 'outline.md', output_path: str = None):
        """
        Main build process

        Args:
            outline_path: Path to outline.md
            output_path: Path for final video (optional)
        """
        self.console.print(
            "\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
        self.console.print(
            f"[bold cyan]  🎬 Video Production Engine v1.0[/bold cyan]")
        self.console.print(
            f"[bold cyan]  Project: {self.config['project']['name']}[/bold cyan]")
        self.console.print(
            "[bold cyan]═══════════════════════════════════════[/bold cyan]\n")

        # Step 1: Parse outline
        self.console.print("[bold]📋 Step 1: Parsing outline...[/bold]")
        parser = OutlineParser(outline_path)
        scenes = parser.parse()

        if not parser.validate():
            self.console.print("[red]✗ Outline validation failed[/red]")
            return

        self.console.print(f"[green]✓ Found {len(scenes)} scenes[/green]")
        self.console.print(
            f"[green]✓ Total duration: {parser.get_total_duration():.1f}s[/green]\n")

        # Step 2: Show plan
        self.console.print("[bold]📊 Step 2: Build plan[/bold]")
        self._show_build_plan(scenes)

        # Step 3: Render scenes
        self.console.print("\n[bold]🎨 Step 3: Rendering scenes...[/bold]")
        rendered_scenes = self._render_scenes(scenes)

        # Step 4: Assemble final video
        self.console.print(
            "\n[bold]🎞️  Step 4: Assembling final video...[/bold]")
        final_path = self._assemble_video(rendered_scenes, output_path)

        # Done
        self.console.print(
            "\n[bold green]✓ Video production complete![/bold green]")
        self.console.print(
            f"[bold green]  Output: {final_path}[/bold green]\n")

    def _show_build_plan(self, scenes: List[Scene]):
        """Display build plan"""
        for i, scene in enumerate(scenes, 1):
            module = self.registry.get_module(scene.__dict__)
            module_name = module.module_type if module else "unknown"

            self.console.print(f"  {i}. [{scene.timestamp}] {scene.title}")
            self.console.print(
                f"     Module: [cyan]{module_name}[/cyan] | Duration: {scene.duration:.1f}s")

            if scene.scene:
                self.console.print(f"     Scene: {scene.scene}")
            if scene.component:
                self.console.print(f"     Component: {scene.component}")
            if scene.clip:
                self.console.print(f"     Clip: {scene.clip}")

            self.console.print()

    def _render_scenes(self, scenes: List[Scene]) -> List[Dict[str, Any]]:
        """Render all scenes"""
        rendered = []

        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
        ) as progress:

            for i, scene in enumerate(scenes, 1):
                task = progress.add_task(
                    f"Rendering {i}/{len(scenes)}: {scene.title}...",
                    total=None
                )

                # Get appropriate module
                module = self.registry.get_module(scene.__dict__)

                if not module:
                    self.console.print(
                        f"[yellow]⚠️  No module found for {scene.title}[/yellow]")
                    continue

                # Render scene
                try:
                    video_path = module.render(scene.__dict__)
                    rendered.append({
                        'scene': scene,
                        'video_path': video_path,
                        'module': module.module_type
                    })
                    progress.update(task, completed=True)
                    self.console.print(f"[green]✓ {scene.title}[/green]")
                except Exception as e:
                    self.console.print(f"[red]✗ {scene.title}: {e}[/red]")

        return rendered

    def _assemble_video(self, rendered_scenes: List[Dict],
                        output_path: str = None) -> Path:
        """Assemble final video using MoviePy"""
        if output_path is None:
            output_dir = Path(self.config['paths']['final_output'])
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{self.config['project']['name']}.mp4"

        # For now, just return the path
        # TODO: Implement actual MoviePy assembly
        self.console.print(
            f"[yellow]ℹ️  MoviePy assembly not yet implemented[/yellow]")
        self.console.print(
            f"[yellow]ℹ️  Individual scenes rendered in renders/ folder[/yellow]")

        return Path(output_path)

    def list_modules(self):
        """List all registered modules"""
        self.console.print("\n[bold]Available modules:[/bold]")
        for module_type in self.registry.list_modules():
            self.console.print(f"  - {module_type}")
        self.console.print()