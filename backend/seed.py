"""Seed the database with initial documents and an admin user from Wasabi S3."""

import os
import re
from io import BytesIO
from app import create_app, db
from app.models.user import User
from app.models.document import Document
from app.services.storage import get_wasabi_storage

# Замена аббревиатур на читаемые названия
ABBREVIATION_MAP = {
    'SHNQ': 'ШНҚ',
    'shnq': 'ШНҚ',
    'KMQ': 'КМҚ',
    'kmq': 'КМҚ',
    'KR': 'КР',
    'kr': 'КР',
}

# Определение категории по коду документа
CATEGORY_PATTERNS = {
    r"(?i)(2710|3\.01|КМК|SHNQ|ШНК).*строител": "Строительство",
    r"(?i)(12\.|ОТ|безопасн)": "Безопасность труда",
    r"(?i)(8\.417|метролог|измерен)": "Метрология",
    r"(?i)(2\.105|2\.301|документ|черте)": "Документация",
    r"(?i)(21\.|проект|план)": "Проектирование",
    r"(?i)(34\.|ит|автомати|техническ.*задан)": "ИТ и автоматизация",
    r"(?i)(30494|микроклимат|жил)": "Строительство",
    r"(?i)(15467|качеств|менеджм)": "Менеджмент качества",
    r"(?i)(материал|бетон|арматур)": "Строительные материалы",
    r"(?i)(электр|энерг)": "Электротехника",
    r"(?i)(вод|канализ|водоснаб)": "Водоснабжение и канализация",
}


def create_readable_title(filename):
    """Создать читаемое название из имени файла."""
    # Убираем 'documents/' и расширение
    base_name = os.path.basename(filename)
    name_without_ext = os.path.splitext(base_name)[0]

    # Заменяем аббревиатуры
    readable = name_without_ext
    for abbr, replacement in ABBREVIATION_MAP.items():
        readable = re.sub(f'\\b{abbr}\\b', replacement, readable, flags=re.IGNORECASE)

    # Заменяем подчеркивания и дефисы на пробелы для лучшей читаемости
    readable = readable.replace('_', ' ').replace('-', ' ')

    # Убираем множественные пробелы
    readable = re.sub(r'\s+', ' ', readable).strip()

    return readable


def extract_pdf_title(pdf_bytes):
    """Попытаться извлечь название из PDF."""
    try:
        import fitz  # PyMuPDF
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")

        # Пробуем получить название из metadata
        metadata_title = pdf.metadata.get('title', '').strip()
        if metadata_title and len(metadata_title) > 5:
            pdf.close()
            return metadata_title

        # Пробуем извлечь из первой страницы
        if pdf.page_count > 0:
            first_page = pdf[0]
            text = first_page.get_text()

            # Берем первые несколько строк
            lines = [line.strip() for line in text.split('\n') if line.strip()]

            # Ищем подходящую строку (длиннее 10 символов, не слишком длинная)
            for line in lines[:10]:
                if 10 < len(line) < 150 and not line.isdigit():
                    pdf.close()
                    return line

        pdf.close()
    except Exception as e:
        print(f"   ⚠ Не удалось извлечь название из PDF: {e}")

    return None


def guess_category(filename):
    """Определить категорию по имени файла."""
    for pattern, category in CATEGORY_PATTERNS.items():
        if re.search(pattern, filename):
            return category
    return "Общие положения"


def extract_year_from_filename(filename):
    """Извлечь год из имени файла (формат: ОзДСт XXXX:2019 или SHNQ-2023)."""
    year_match = re.search(r"[:\-](\d{4})", filename)
    if year_match:
        return int(year_match.group(1))
    return None


def extract_code_from_filename(filename):
    """Извлечь код документа (до расширения)."""
    return os.path.splitext(filename)[0]


def get_pdf_page_count(pdf_bytes):
    """Получить количество страниц в PDF."""
    try:
        import fitz  # PyMuPDF
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = pdf.page_count
        pdf.close()
        return page_count
    except Exception as e:
        print(f"   ⚠ Не удалось определить количество страниц: {e}")
        return 10  # Значение по умолчанию


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Admin user
        if not User.query.filter_by(email="admin@standards.uz").first():
            admin = User(email="admin@standards.uz", name="Администратор", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            print("+ Создан администратор: admin@standards.uz / admin123")

        # Load documents from Wasabi S3
        wasabi = get_wasabi_storage()
        print("\n🔍 Загрузка документов из Wasabi S3...")

        try:
            s3_files = wasabi.list_files()
            print(f"   Найдено файлов в S3: {len(s3_files)}")

            added_count = 0
            for s3_file in s3_files:
                filename = s3_file['Key']

                # Пропускаем не-PDF файлы
                if not filename.lower().endswith('.pdf'):
                    continue

                # Извлекаем метаданные
                code = extract_code_from_filename(filename)
                year = extract_year_from_filename(filename)
                category = guess_category(filename)

                # Проверяем, существует ли документ (по file_path)
                existing = Document.query.filter_by(file_path=filename).first()
                if existing:
                    print(f"   ⏭ Пропущен (уже есть): {filename}")
                    continue

                print(f"   📄 Обработка: {filename}")

                # Скачиваем PDF чтобы определить количество страниц и название
                try:
                    pdf_bytes = wasabi.download_file(filename)
                    page_count = get_pdf_page_count(BytesIO(pdf_bytes))

                    # Пытаемся извлечь человекочитаемое название
                    pdf_title = extract_pdf_title(pdf_bytes)
                    if pdf_title:
                        readable_title = pdf_title
                        print(f"   ✓ Извлечено название из PDF: {readable_title[:50]}...")
                    else:
                        readable_title = create_readable_title(filename)
                        print(f"   ✓ Создано название из файла: {readable_title}")
                except Exception as e:
                    print(f"   ⚠ Ошибка при скачивании: {e}")
                    page_count = 10  # Значение по умолчанию
                    readable_title = create_readable_title(filename)

                # Создаем документ (используем поля из модели Document)
                document = Document(
                    title=readable_title,  # Человекочитаемое название
                    category=category,
                    pages=page_count,  # Document.pages (не page_count)
                    year=year if year else 2020,  # year обязателен
                    file_path=filename,
                    description=f"Государственный стандарт {code}"
                )

                db.session.add(document)
                print(f"   ✅ Добавлен: {code} ({page_count} стр, {category})")
                added_count += 1

            db.session.commit()
            print(f"\n✅ Готово! Добавлено документов: {added_count}")

        except Exception as e:
            print(f"\n❌ Ошибка при загрузке из Wasabi: {e}")
            print("   Создаем базу данных без документов...")
            db.session.commit()


if __name__ == "__main__":
    seed()
