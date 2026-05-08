"""Синхронизация ограниченного количества документов для тестирования."""

import os
import sys
from app import create_app, db
from app.models.document import Document
from app.services.storage import get_wasabi_storage
import requests

AI_BACKEND_URL = "http://ai-backend:8000"

# Количество документов для синхронизации (по умолчанию 10)
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 10


def sync_document_to_ai(document, pdf_bytes):
    """Отправить один документ в AI backend."""
    try:
        # Генерируем code из file_path
        code = os.path.splitext(os.path.basename(document.file_path))[0] if document.file_path else str(document.id)

        # Отправляем PDF файл в Django AI backend
        files = {
            'file': (f'{document.id}.pdf', pdf_bytes, 'application/pdf')
        }
        data = {
            'document_id': document.id,
            'title': document.title,
            'code': code,
            'category': document.category,
            'year': document.year,
            'file_path': document.file_path,
        }

        response = requests.post(
            f"{AI_BACKEND_URL}/api/sync-document/",
            files=files,
            data=data,
            timeout=300
        )

        if response.status_code == 200:
            return True, "Успешно"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"

    except Exception as e:
        return False, str(e)


def sync_limited():
    """Синхронизировать ограниченное количество документов."""
    app = create_app()
    with app.app_context():
        documents = Document.query.limit(LIMIT).all()
        total = len(documents)
        print(f"\n🔄 Синхронизация первых {total} документов с AI backend...\n")

        wasabi = get_wasabi_storage()
        success_count = 0
        error_count = 0

        for idx, doc in enumerate(documents, 1):
            print(f"[{idx}/{total}] {doc.title[:50]}...")

            if not doc.file_path:
                print(f"   ⏭ Пропущен - нет file_path")
                continue

            try:
                # Скачиваем PDF из Wasabi
                pdf_bytes = wasabi.download_file(doc.file_path)
                print(f"   ⬇ Скачан из Wasabi ({len(pdf_bytes)} bytes)")

                # Отправляем в AI backend
                success, message = sync_document_to_ai(doc, pdf_bytes)

                if success:
                    print(f"   ✅ {message}")
                    success_count += 1
                else:
                    print(f"   ❌ Ошибка: {message}")
                    error_count += 1

            except Exception as e:
                print(f"   ❌ Ошибка обработки: {e}")
                error_count += 1

        print(f"\n{'='*60}")
        print(f"✅ Успешно: {success_count}")
        print(f"❌ Ошибок: {error_count}")
        print(f"📊 Всего: {total}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    sync_limited()
