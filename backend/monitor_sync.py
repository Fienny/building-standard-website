"""Мониторинг прогресса синхронизации с AI backend."""

import time
import requests
from app import create_app, db
from app.models.document import Document

AI_BACKEND_URL = "http://ai-backend:8000"


def get_flask_stats():
    """Получить статистику из Flask БД."""
    app = create_app()
    with app.app_context():
        total = Document.query.count()
        return {'total': total}


def get_django_stats():
    """Получить статистику из Django AI backend."""
    try:
        # Можно было бы сделать API endpoint, но пока через подсчет в Django shell
        # Для простоты будем просто показывать что Flask имеет
        return {'synced': '?', 'clauses': '?', 'embeddings': '?'}
    except Exception as e:
        return {'error': str(e)}


def monitor():
    """Запустить мониторинг в реальном времени."""
    print("📊 Мониторинг синхронизации")
    print("Нажмите Ctrl+C для выхода\n")
    print(f"{'='*70}")

    try:
        while True:
            flask_stats = get_flask_stats()

            print(f"\r⏱ {time.strftime('%H:%M:%S')} | "
                  f"Flask документов: {flask_stats['total']} | "
                  f"Проверьте Django logs для деталей...", end='', flush=True)

            time.sleep(5)  # Обновление каждые 5 секунд

    except KeyboardInterrupt:
        print("\n\n✅ Мониторинг остановлен")


if __name__ == "__main__":
    monitor()
