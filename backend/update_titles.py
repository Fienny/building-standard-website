"""Обновить названия документов на читаемые."""

import os
import re
from io import BytesIO
from app import create_app, db
from app.models.document import Document
from app.services.storage import get_wasabi_storage

# Замена аббревиатур
ABBREVIATION_MAP = {
    'SHNQ': 'ШНҚ',
    'shnq': 'ШНҚ',
    'KMQ': 'КМҚ',
    'kmq': 'КМҚ',
    'KR': 'КР',
    'kr': 'КР',
}


def create_readable_title(filename):
    """Создать читаемое название из имени файла."""
    base_name = os.path.basename(filename)
    name_without_ext = os.path.splitext(base_name)[0]

    # Заменяем аббревиатуры
    readable = name_without_ext
    for abbr, replacement in ABBREVIATION_MAP.items():
        readable = re.sub(f'\\b{abbr}\\b', replacement, readable, flags=re.IGNORECASE)

    # Заменяем подчеркивания на пробелы, но сохраняем точки и цифры
    readable = readable.replace('_', ' ')

    # Убираем множественные пробелы
    readable = re.sub(r'\s+', ' ', readable).strip()

    return readable


def extract_pdf_title(pdf_bytes):
    """Попытаться извлечь название из PDF."""
    try:
        import fitz
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")

        # Metadata
        metadata_title = pdf.metadata.get('title', '').strip()
        if metadata_title and len(metadata_title) > 5:
            pdf.close()
            return metadata_title

        # Первая страница
        if pdf.page_count > 0:
            first_page = pdf[0]
            text = first_page.get_text()
            lines = [line.strip() for line in text.split('\n') if line.strip()]

            for line in lines[:10]:
                if 10 < len(line) < 150 and not line.isdigit():
                    pdf.close()
                    return line

        pdf.close()
    except Exception as e:
        print(f"   ⚠ Ошибка извлечения: {e}")

    return None


def update_titles():
    """Обновить все названия документов."""
    app = create_app()
    with app.app_context():
        documents = Document.query.all()
        print(f"\n📝 Найдено документов: {len(documents)}\n")

        wasabi = get_wasabi_storage()
        updated = 0

        for doc in documents:
            if not doc.file_path:
                continue

            old_title = doc.title

            # Пробуем извлечь из PDF
            try:
                print(f"   📄 {doc.file_path}")
                pdf_bytes = wasabi.download_file(doc.file_path)
                pdf_title = extract_pdf_title(pdf_bytes)

                if pdf_title:
                    new_title = pdf_title
                    print(f"      ✓ Из PDF: {new_title[:60]}...")
                else:
                    new_title = create_readable_title(doc.file_path)
                    print(f"      ✓ Из файла: {new_title}")

                doc.title = new_title
                updated += 1

            except Exception as e:
                print(f"      ⚠ Ошибка: {e}")
                # Если не удалось скачать - хотя бы имя файла
                new_title = create_readable_title(doc.file_path)
                doc.title = new_title
                updated += 1

        db.session.commit()
        print(f"\n✅ Обновлено: {updated} документов")


if __name__ == "__main__":
    update_titles()
