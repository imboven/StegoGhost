#!/usr/bin/env python3
"""
Скрипт для сборки StegoGhost в исполняемый файл
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build():
    """Очистка папок сборки"""
    print("🧹 Очистка предыдущих сборок...")
    
    folders_to_clean = ['build', 'dist', '__pycache__']
    for folder in folders_to_clean:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"   Удалена папка: {folder}")
            except Exception as e:
                print(f"   ⚠️  Не удалось удалить {folder}: {e}")
    
    # Удаление .pyc файлов
    try:
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.pyc'):
                    try:
                        os.remove(os.path.join(root, file))
                    except Exception:
                        pass  # Игнорируем ошибки удаления .pyc файлов
        print("   ✅ Временные файлы очищены")
    except Exception as e:
        print(f"   ⚠️  Ошибка при очистке .pyc файлов: {e}")
    
    return True

def check_dependencies():
    """Проверка установленных зависимостей"""
    print("🔍 Проверка зависимостей...")
    
    # Словарь с правильными именами для импорта
    required_packages = {
        'PyInstaller': 'PyInstaller',
        'Pillow': 'PIL',
        'cryptography': 'cryptography', 
        'PyQt5': 'PyQt5',
        'numpy': 'numpy',
        'psutil': 'psutil'
    }
    
    missing_packages = []
    
    for display_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"   ✅ {display_name}")
        except ImportError:
            missing_packages.append(display_name)
            print(f"   ❌ {display_name}")
    
    if missing_packages:
        print(f"\n❗ Не найдены пакеты: {', '.join(missing_packages)}")
        print("   Установите их командой: pip install " + " ".join(missing_packages))
        return False
    
    return True

def build_application():
    """Сборка приложения с PyInstaller"""
    print("🔨 Начинаем сборку приложения...")
    
    # Команда для PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'StegoGhost.spec'
    ]
    
    print(f"   Выполняем: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("   ✅ Сборка завершена успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Ошибка сборки: {e}")
        print(f"   Вывод: {e.stdout}")
        print(f"   Ошибки: {e.stderr}")
        return False

def create_release():
    """Создание папки релиза"""
    print("📦 Создание релиза...")
    
    dist_exe = Path('dist/StegoGhost.exe')
    if not dist_exe.exists():
        print("   ❌ Исполняемый файл не найден!")
        return False
    
    # Создание папки релиза
    release_dir = Path('StegoGhost_Release')
    release_dir.mkdir(exist_ok=True)
    
    # Копирование исполняемого файла
    shutil.copy2(dist_exe, release_dir)
    
    print(f"   ✅ Исполняемый файл скопирован")
    
    # Создание README для релиза
    readme_content = """# StegoGhost

Стеганографическое приложение для сокрытия данных в изображениях.

## Использование
1. Запустите StegoGhost.exe
2. Выберите изображение-контейнер
3. Введите секретное сообщение
4. Установите пароль
5. Нажмите "Скрыть и сохранить" или "Извлечь сообщение"

## Возможности
- Скрытие текстовых сообщений в изображениях
- Шифрование AES-256 с защитой паролем
- Поддержка PNG, JPEG, WebP форматов
- Современный интерфейс с темной темой

## Системные требования
- Windows 7/8/10/11
- Минимум 100 МБ свободного места
"""
    
    with open(release_dir / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"   ✅ Релиз создан в папке: {release_dir}")
    print(f"   📁 Размер файла: {dist_exe.stat().st_size / (1024*1024):.1f} МБ")
    
    return True

def main():
    """Главная функция сборки"""
    print("🚀 StegoGhost Builder v1.0")
    print("=" * 40)
    
    # Проверка что мы в правильной директории
    if not Path('main.py').exists():
        print("❌ Не найден main.py! Запустите скрипт из корня проекта.")
        return False
    
    # Пошаговая сборка
    steps = [
        ("Очистка", clean_build),
        ("Проверка зависимостей", check_dependencies),
        ("Сборка приложения", build_application),
        ("Создание релиза", create_release)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 Шаг: {step_name}")
        if not step_func():
            print(f"❌ Ошибка на шаге: {step_name}")
            return False
    
    print("\n🎉 Сборка завершена успешно!")
    print("   Исполняемый файл: StegoGhost_Release/StegoGhost.exe")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 