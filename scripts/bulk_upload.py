#!/usr/bin/env python3
"""
Bulk upload скрипт для загрузки всех документов из архива.
Поддерживает:
- синхронизацию с AI backend
- Telegram-уведомления о статусе
- manifest CSV для ручного title/category/description/language
"""
import csv
import sys
from pathlib import Path
from typing import Dict

# Добавляем backend в Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app import create_app, db
from app.models.document import Document
from app.services.document_processor import DocumentProcessor
from app.services.ai_sync import AIBackendSync
from telegram_notifier import TelegramNotifier


def _load_manifest(manifest_path: str | None) -> Dict[str, Dict]:
    if not manifest_path:
        return {}

    path = Path(manifest_path)
    if not path.exists():
        raise FileNotFoundError(f"Manifest не найден: {manifest_path}")

    mapping: Dict[str, Dict] = {}
    with path.open('r', encoding='utf-8-sig', newline='') as file_obj:
        reader = csv.DictReader(file_obj)
        for row in reader:
            filename = (row.get('source_filename') or '').strip()
            if not filename:
                continue
            mapping[filename] = {
                'title': (row.get('title') or '').strip(),
                'category': (row.get('category') or '').strip(),
                'description': (row.get('description') or '').strip(),
                'language': (row.get('language') or '').strip().lower(),
            }

    return mapping


def bulk_upload(documents_dir: str, sync_ai: bool = True, manifest_path: str | None = None):
    """
    Массовая загрузка документов.

    Args:
        documents_dir: Путь к папке с документами
        sync_ai: Синхронизировать с AI backend
        manifest_path: CSV с ручными метаданными по filename
    """
    app = create_app()
    notifier = TelegramNotifier(process_name="bulk_upload")

    with app.app_context():
        docs_path = Path(documents_dir)

        if not docs_path.exists():
            message = f"Папка не найдена: {documents_dir}"
            print(f"❌ {message}")
            notifier.error(message)
            return

        try:
            manifest = _load_manifest(manifest_path)
        except Exception as exc:
            print(f"❌ Ошибка чтения manifest: {exc}")
            notifier.error(f"Ошибка чтения manifest: {exc}")
            return

        files = list(docs_path.glob('*.pdf'))
        files += list(docs_path.glob('*.doc'))
        files += list(docs_path.glob('*.docx'))

        print(f"📂 Найдено файлов: {len(files)}")
        print(f"📁 Папка: {docs_path}")
        print(f"🤖 AI синхронизация: {'Вкл' if sync_ai else 'Выкл'}")
        print(f"🧾 Manifest: {manifest_path or 'не используется'}")
        print("\n" + "="*60)

        notifier.info(
            f"Старт загрузки\nПапка: {docs_path}\nФайлов: {len(files)}\n"
            f"AI sync: {'on' if sync_ai else 'off'}\nManifest: {manifest_path or 'none'}"
        )

        processor = DocumentProcessor(app.config['UPLOAD_FOLDER'])
        ai_sync = AIBackendSync(app.config['AI_BACKEND_URL']) if sync_ai else None

        stats = {
            'success': 0,
            'converted': 0,
            'ai_synced': 0,
            'ai_failed': 0,
            'errors': 0,
            'skipped': 0,
        }

        for idx, file_path in enumerate(sorted(files), 1):
            print(f"\n[{idx}/{len(files)}] 🔄 {file_path.name}")

            try:
                with open(file_path, 'rb') as file_obj:
                    class FileWrapper:
                        def __init__(self, f_obj, filename):
                            self.file = f_obj
                            self.filename = filename

                        def save(self, path):
                            with open(path, 'wb') as dest:
                                dest.write(self.file.read())

                    overrides = manifest.get(file_path.name, {})
                    result = processor.process_upload(
                        FileWrapper(file_obj, file_path.name),
                        manual_title=overrides.get('title', ''),
                        manual_category=overrides.get('category', ''),
                        manual_description=overrides.get('description', ''),
                    )

                    if result['status'] == 'error':
                        print(f"   ❌ Ошибка: {result['message']}")
                        stats['errors'] += 1
                        continue

                    existing = Document.query.filter_by(title=result['title']).first()
                    if existing:
                        print("   ⚠️  Уже существует (пропуск)")
                        stats['skipped'] += 1
                        continue

                    document = Document(
                        title=result['title'],
                        category=result['category'],
                        year=result['year'],
                        pages=result['pages'],
                        description=result['description'],
                        file_path=result['file_path'],
                        is_active=True,
                    )

                    if 'language' in Document.__table__.columns and overrides.get('language'):
                        document.language = overrides['language']

                    db.session.add(document)
                    db.session.commit()

                    print(f"   ✅ {result['title']} ({result['pages']} стр.)")
                    stats['success'] += 1

                    if str(result.get('original_filename', '')).lower().endswith(('.doc', '.docx')):
                        stats['converted'] += 1

                    if ai_sync:
                        try:
                            sync_result = ai_sync.sync_document(document)
                            if sync_result['status'] == 'success':
                                print("   🤖 AI синхронизирован")
                                stats['ai_synced'] += 1
                            else:
                                print(f"   ⚠️  AI ошибка: {sync_result.get('message')}")
                                stats['ai_failed'] += 1
                        except Exception as exc:
                            print(f"   ⚠️  AI недоступен: {exc}")
                            stats['ai_failed'] += 1

            except Exception as exc:
                print(f"   ❌ Ошибка обработки: {exc}")
                stats['errors'] += 1

        print("\n" + "="*60)
        print("📊 ИТОГОВАЯ СТАТИСТИКА")
        print("="*60)
        print(f"Всего файлов:           {len(files)}")
        print(f"✅ Успешно загружено:   {stats['success']}")
        print(f"📄 Конвертировано:      {stats['converted']}")
        print(f"🤖 AI синхронизировано: {stats['ai_synced']}")
        print(f"⚠️  AI ошибки:          {stats['ai_failed']}")
        print(f"⏭️  Пропущено:          {stats['skipped']}")
        print(f"❌ Ошибки обработки:    {stats['errors']}")
        print("="*60)

        total_docs = Document.query.count()
        print(f"\n📚 Всего документов в БД: {total_docs}")

        summary = (
            f"Всего файлов: {len(files)}\n"
            f"Успешно: {stats['success']}\n"
            f"Пропущено: {stats['skipped']}\n"
            f"Ошибки: {stats['errors']}\n"
            f"AI ok/failed: {stats['ai_synced']}/{stats['ai_failed']}\n"
            f"Всего в БД: {total_docs}"
        )

        if stats['errors'] > 0:
            notifier.warning(f"Загрузка завершена с ошибками\n{summary}")
        else:
            notifier.success(f"Загрузка завершена успешно\n{summary}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Массовая загрузка документов в Flask backend'
    )
    parser.add_argument('directory', help='Путь к папке с документами (PDF/DOC/DOCX)')
    parser.add_argument('--no-ai', action='store_true', help='Не синхронизировать с AI backend')
    parser.add_argument(
        '--manifest',
        help='Путь к CSV manifest (source_filename,title,category,description,language)',
        default=None,
    )

    args = parser.parse_args()
    bulk_upload(args.directory, sync_ai=not args.no_ai, manifest_path=args.manifest)


if __name__ == "__main__":
    main()
