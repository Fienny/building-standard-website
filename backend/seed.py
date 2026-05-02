"""Seed the database with initial documents and an admin user from Wasabi S3."""

import os
import re
from io import BytesIO
from app import create_app, db
from app.models.user import User
from app.models.document import Document
from app.services.wasabi_service import WasabiService

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
        wasabi = WasabiService()
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

                # Проверяем, существует ли документ
                existing = Document.query.filter_by(code=code).first()
                if existing:
                    print(f"   ⏭ Пропущен (уже есть): {code}")
                    continue

                print(f"   📄 Обработка: {filename}")

                # Скачиваем PDF чтобы определить количество страниц
                try:
                    pdf_bytes = wasabi.download_file(filename)
                    page_count = get_pdf_page_count(BytesIO(pdf_bytes))
                except Exception as e:
                    print(f"   ⚠ Ошибка при скачивании: {e}")
                    page_count = 10  # Значение по умолчанию

                # Создаем документ
                document = Document(
                    code=code,
                    title_ru=code,  # Можно улучшить, парсив имя файла
                    category=category,
                    page_count=page_count,
                    year=year,
                    language='ru',
                    file_path=filename,
                    wasabi_key=filename,
                    file_size=s3_file.get('Size', 0),
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
