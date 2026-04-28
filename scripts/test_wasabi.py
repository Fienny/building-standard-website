#!/usr/bin/env python3
"""
Тестовый скрипт для проверки подключения к Wasabi storage
"""
import sys
import os
from pathlib import Path
from io import BytesIO

# Добавляем backend в Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from dotenv import load_dotenv

# Загружаем .env из backend
env_path = Path(__file__).parent.parent / 'backend' / '.env'
load_dotenv(env_path)

from app.services.storage import WasabiStorage


def test_wasabi_connection():
    """Тестирует подключение к Wasabi"""
    print("=" * 60)
    print("🧪 ТЕСТ ПОДКЛЮЧЕНИЯ К WASABI STORAGE")
    print("=" * 60)

    # Проверяем переменные окружения
    access_key = os.getenv('WASABI_ACCESS_KEY_ID')
    secret_key = os.getenv('WASABI_SECRET_ACCESS_KEY')
    bucket_name = os.getenv('WASABI_BUCKET_NAME')
    region = os.getenv('WASABI_REGION', 'eu-central-1')

    print(f"\n📋 Конфигурация:")
    print(f"   Bucket:  {bucket_name}")
    print(f"   Region:  {region}")
    print(f"   Access Key: {access_key[:10]}..." if access_key else "   Access Key: NOT SET")
    print(f"   Secret Key: {'*' * 20}" if secret_key else "   Secret Key: NOT SET")

    if not all([access_key, secret_key, bucket_name]):
        print("\n❌ ОШИБКА: Не все переменные окружения настроены")
        print("   Проверьте backend/.env файл")
        return False

    try:
        # Инициализируем storage
        storage = WasabiStorage(
            access_key=access_key,
            secret_key=secret_key,
            bucket_name=bucket_name,
            region=region
        )
        print("\n✅ Storage инициализирован")

        # Тест 1: Загрузка тестового файла
        print("\n📤 Тест 1: Загрузка тестового файла...")
        test_content = b"Test document content for Wasabi storage verification"
        test_file = BytesIO(test_content)
        test_object_name = "test/test_file.txt"

        url = storage.upload_file(test_file, test_object_name, content_type='text/plain')

        if url:
            print(f"   ✅ Файл загружен!")
            print(f"   URL: {url}")
        else:
            print("   ❌ Ошибка загрузки")
            return False

        # Тест 2: Проверка существования файла
        print("\n🔍 Тест 2: Проверка существования файла...")
        exists = storage.file_exists(test_object_name)
        if exists:
            print("   ✅ Файл найден в bucket")
        else:
            print("   ❌ Файл не найден")
            return False

        # Тест 3: Получение URL файла
        print("\n🔗 Тест 3: Получение публичного URL...")
        public_url = storage.get_file_url(test_object_name)
        print(f"   URL: {public_url}")
        if public_url:
            print("   ✅ URL получен")
        else:
            print("   ❌ Ошибка получения URL")
            return False

        # Тест 4: Список файлов в папке test/
        print("\n📋 Тест 4: Список файлов в папке test/...")
        files = storage.list_files(prefix='test/')
        print(f"   Найдено файлов: {len(files)}")
        for f in files:
            print(f"      - {f}")
        if files:
            print("   ✅ Список получен")
        else:
            print("   ⚠️  Папка пустая или не найдена")

        # Тест 5: Удаление тестового файла
        print("\n🗑️  Тест 5: Удаление тестового файла...")
        deleted = storage.delete_file(test_object_name)
        if deleted:
            print("   ✅ Файл удалён")
        else:
            print("   ❌ Ошибка удаления")
            return False

        # Проверяем что файл действительно удалён
        exists_after = storage.file_exists(test_object_name)
        if not exists_after:
            print("   ✅ Подтверждено удаление")
        else:
            print("   ⚠️  Файл всё ещё существует")

        print("\n" + "=" * 60)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 60)
        print("\n📌 Wasabi storage готов к использованию")
        print(f"📌 Bucket: {bucket_name}")
        print(f"📌 Region: {region}")
        print(f"📌 Endpoint: https://s3.{region}.wasabisys.com")
        print("\n✅ Можно запускать bulk_upload.py для загрузки документов")
        return True

    except Exception as e:
        print(f"\n❌ ОШИБКА: {str(e)}")
        print("\nВозможные причины:")
        print("  1. Неверные credentials (Access Key / Secret Key)")
        print("  2. Bucket не существует или неверное имя")
        print("  3. Проблемы с сетью / firewall")
        print("  4. Неверный регион")
        return False


if __name__ == "__main__":
    success = test_wasabi_connection()
    sys.exit(0 if success else 1)
