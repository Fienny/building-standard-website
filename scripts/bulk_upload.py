#!/usr/bin/env python3
"""
Bulk upload скрипт для загрузки всех документов из архива
Использует DocumentProcessor для автоматической обработки
"""
import sys
import os
from pathlib import Path

# Добавляем backend в Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app import create_app, db
from app.models.document import Document
from app.services.document_processor import DocumentProcessor
from app.services.ai_sync import AIBackendSync
from app.services.storage import get_wasabi_storage


def bulk_upload(documents_dir: str, sync_ai: bool = True):
    """
    Массовая загрузка документов

    Args:
        documents_dir: Путь к папке с документами
        sync_ai: Синхронизировать с AI backend
    """
    app = create_app()

    with app.app_context():
        docs_path = Path(documents_dir)

        if not docs_path.exists():
            print(f"❌ Папка не найдена: {documents_dir}")
            return

        # Находим все PDF и DOC/DOCX файлы
        files = list(docs_path.glob('*.pdf'))
        files += list(docs_path.glob('*.doc'))
        files += list(docs_path.glob('*.docx'))

        print(f"📂 Найдено файлов: {len(files)}")
        print(f"📁 Папка: {docs_path}")
        print(f"🤖 AI синхронизация: {'Вкл' if sync_ai else 'Выкл'}")
        print("\n" + "="*60)

        # Инициализируем процессор с Wasabi storage
        storage = get_wasabi_storage()
        processor = DocumentProcessor(app.config['UPLOAD_FOLDER'], storage=storage)
        ai_sync = AIBackendSync(app.config['AI_BACKEND_URL']) if sync_ai else None

        stats = {
            'success': 0,
            'converted': 0,
            'ai_synced': 0,
            'ai_failed': 0,
            'errors': 0,
        }

        for idx, file_path in enumerate(sorted(files), 1):
            print(f"\n[{idx}/{len(files)}] 🔄 {file_path.name}")

            try:
                # Открываем файл
                with open(file_path, 'rb') as f:
                    # Создаём объект файла для процессора
                    class FileWrapper:
                        def __init__(self, file_obj, filename):
                            self.file = file_obj
                            self.filename = filename

                        def save(self, path):
                            with open(path, 'wb') as dest:
                                dest.write(self.file.read())

                        def read(self):
                            return self.file.read()

                    file_wrapper = FileWrapper(f, file_path.name)

                    # Обрабатываем документ
                    result = processor.process_upload(file_wrapper)

                    if result['status'] == 'error':
                        print(f"   ❌ Ошибка: {result['message']}")
                        stats['errors'] += 1
                        continue

                    # Проверяем дубликат
                    existing = Document.query.filter_by(title=result['title']).first()
                    if existing:
                        print(f"   ⚠️  Уже существует (пропуск)")
                        continue

                    # Создаём запись в БД
                    document = Document(
                        title=result['title'],
                        category=result['category'],
                        year=result['year'],
                        pages=result['pages'],
                        description=result['description'],
                        file_path=result['file_path'],
                        is_active=True
                    )

                    db.session.add(document)
                    db.session.commit()

                    print(f"   ✅ {result['title']} ({result['pages']} стр.)")
                    stats['success'] += 1

                    if result.get('original_filename', '').endswith(('.doc', '.docx')):
                        stats['converted'] += 1

                    # Синхронизация с AI
                    if ai_sync:
                        try:
                            sync_result = ai_sync.sync_document(document)
                            if sync_result['status'] == 'success':
                                print(f"   🤖 AI синхронизирован")
                                stats['ai_synced'] += 1
                            else:
                                print(f"   ⚠️  AI ошибка: {sync_result.get('message')}")
                                stats['ai_failed'] += 1
                        except Exception as e:
                            print(f"   ⚠️  AI недоступен: {str(e)}")
                            stats['ai_failed'] += 1

            except Exception as e:
                print(f"   ❌ Ошибка обработки: {str(e)}")
                stats['errors'] += 1
                continue

        # Итоговая статистика
        print("\n" + "="*60)
        print("📊 ИТОГОВАЯ СТАТИСТИКА")
        print("="*60)
        print(f"Всего файлов:           {len(files)}")
        print(f"✅ Успешно загружено:   {stats['success']}")
        print(f"📄 Конвертировано:      {stats['converted']}")
        print(f"🤖 AI синхронизировано:  {stats['ai_synced']}")
        print(f"⚠️  AI ошибки:          {stats['ai_failed']}")
        print(f"❌ Ошибки обработки:    {stats['errors']}")
        print("="*60)

        # Проверка БД
        total_docs = Document.query.count()
        print(f"\n📚 Всего документов в БД: {total_docs}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Массовая загрузка документов в Flask backend'
    )
    parser.add_argument(
        'directory',
        help='Путь к папке с документами (PDF/DOC/DOCX)'
    )
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Не синхронизировать с AI backend'
    )

    args = parser.parse_args()

    bulk_upload(args.directory, sync_ai=not args.no_ai)


if __name__ == "__main__":
    main()
