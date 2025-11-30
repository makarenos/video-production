#!/usr/bin/env python3
"""
Скрипт проверки и установки зависимостей
"""

import subprocess
import sys
import os

def check_command(command):
    """Проверяет наличие команды в системе"""
    try:
        subprocess.run([command, '--version'], 
                      capture_output=True, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_python_package(package):
    """Проверяет установлен ли Python пакет"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def main():
    """Проверка всех зависимостей"""
    
    print("\n" + "="*60)
    print("  Проверка зависимостей для видеоавтоматизации")
    print("="*60 + "\n")
    
    # Системные команды
    print("📦 Системные утилиты:")
    system_tools = {
        'ffmpeg': 'FFmpeg',
        'python3': 'Python 3',
        'node': 'Node.js',
        'npm': 'NPM'
    }
    
    for cmd, name in system_tools.items():
        status = "✓" if check_command(cmd) else "✗"
        print(f"  {status} {name}")
    
    print()
    
    # Python пакеты
    print("🐍 Python библиотеки:")
    python_packages = {
        'yaml': 'PyYAML',
        'PIL': 'Pillow',
        'manim': 'Manim',
        'moviepy': 'MoviePy',
        'rich': 'Rich'
    }
    
    for pkg, name in python_packages.items():
        status = "✓" if check_python_package(pkg) else "✗"
        print(f"  {status} {name}")
    
    print("\n" + "="*60)
    print("  Установка отсутствующих зависимостей")
    print("="*60 + "\n")
    
    # Установка Python пакетов
    missing_packages = []
    for pkg, name in python_packages.items():
        if not check_python_package(pkg):
            missing_packages.append(pkg if pkg != 'PIL' else 'pillow')
    
    if missing_packages:
        print(f"Установка: {', '.join(missing_packages)}\n")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                '--break-system-packages',
                *missing_packages
            ], check=True)
            print("\n✓ Python пакеты установлены успешно!")
        except subprocess.CalledProcessError:
            print("\n✗ Ошибка установки Python пакетов")
    else:
        print("✓ Все Python пакеты уже установлены!")
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()
