"""
Автоматическая обработка документов:
- Нормализация названий файлов
- Конвертация DOC/DOCX → PDF
- Подсчёт страниц
- Извлечение метаданных
- Загрузка в Wasabi S3 storage
"""
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
from .storage import WasabiStorage


class DocumentProcessor:
    """Процессор документов с автоматической нормализацией"""

    # Паттерны для извлечения кода документа
    CODE_PATTERNS = [
        r'SHNQ[\s_-]+(\d+\.\d+\.\d+[-_]\d+)',
        r'shnq[\s_-]+(\d+\.\d+\.\d+[-_]\d+)',
        r'[KkКк][MmМм][QqҚқ][\s_-]+(\d+\.\d+\.\d+[-_]\d+)',
        r'[KkКк][RrРр][\s_-]+(\d+\.\d+[-_]\d+)',
        r'shnk[-_](\d+\.\d+\.\d+[-_]\d+)',
        r'^(\d+\.\d+\.\d+[-_]\d+)',
    ]

    # Категории документов
    CATEGORIES = {
        'SHNQ': 'Строительство',
        'KMQ': 'Качество и метрология',
        'KR': 'Конструкции и расчёты',
    }

    def __init__(self, upload_folder: str, storage: Optional[WasabiStorage] = None):
        self.upload_folder = Path(upload_folder)
        self.upload_folder.mkdir(parents=True, exist_ok=True)
        self.storage = storage

    def extract_code(self, filename: str) -> Optional[Tuple[str, str]]:
        """
        Извлекает код документа из названия
        Returns: (prefix, code) или None
        """
        filename_lower = filename.lower()

        for pattern in self.CODE_PATTERNS:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                code = match.group(1).replace('_', '-')

                # Определяем префикс
                if 'shnq' in filename_lower or 'shnk' in filename_lower:
                    prefix = 'SHNQ'
                elif any(x in filename_lower for x in ['kmq', 'kmk', 'кмқ', 'кмк']):
                    prefix = 'KMQ'
                elif any(x in filename_lower for x in ['kr', 'кр']):
                    prefix = 'KR'
                else:
                    prefix = 'SHNQ'

                return prefix, code

        return None

    def normalize_filename(self, original_filename: str) -> str:
        """
        Нормализует название файла
        Example: "shnk-1.02.07-19-uzb.rus.pdf" → "SHNQ_1.02.07-19.pdf"
        """
        code_info = self.extract_code(original_filename)

        if code_info:
            prefix, code = code_info
            return f"{prefix}_{code}.pdf"

        # Если не удалось извлечь код - используем безопасное имя
        return secure_filename(original_filename)

    def convert_doc_to_pdf(self, doc_path: Path) -> Optional[Path]:
        """
        Конвертирует DOC/DOCX в PDF через LibreOffice
        """
        try:
            output_dir = doc_path.parent

            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', str(output_dir),
                str(doc_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                pdf_path = doc_path.with_suffix('.pdf')
                if pdf_path.exists():
                    # Удаляем оригинальный DOC/DOCX
                    doc_path.unlink()
                    return pdf_path

            return None

        except Exception:
            return None

    def count_pages(self, pdf_path: Path) -> int:
        """Подсчитывает количество страниц в PDF"""
        try:
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()
            return page_count
        except Exception:
            return 0

    def extract_year(self, code: str) -> int:
        """
        Извлекает год из кода документа
        Example: "2.01.01-22" → 2022
        """
        match = re.search(r'[-_](\d{2})$', code)
        if match:
            year_suffix = int(match.group(1))
            # Преобразуем 2-значный год в 4-значный
            return 2000 + year_suffix if year_suffix < 50 else 1900 + year_suffix
        # Если год не найден - возвращаем текущий год как дефолт
        from datetime import datetime
        return datetime.now().year

    def process_upload(
        self,
        file,
        manual_title: str = '',
        manual_category: str = '',
        manual_description: str = ''
    ) -> Dict:
        """
        Полная обработка загруженного файла
        """
        try:
            original_filename = file.filename
            file_ext = Path(original_filename).suffix.lower()

            # Проверка формата
            if file_ext not in ['.pdf', '.doc', '.docx']:
                return {
                    'status': 'error',
                    'message': 'Неподдерживаемый формат файла. Используйте PDF, DOC или DOCX.'
                }

            # Сохраняем временно с оригинальным названием
            temp_filename = secure_filename(original_filename)
            temp_path = self.upload_folder / temp_filename
            file.save(temp_path)

            # Конвертируем DOC/DOCX → PDF
            if file_ext in ['.doc', '.docx']:
                pdf_path = self.convert_doc_to_pdf(temp_path)
                if not pdf_path:
                    temp_path.unlink()  # Удаляем temp file
                    return {
                        'status': 'error',
                        'message': 'Ошибка конвертации DOC/DOCX в PDF. Установите LibreOffice.'
                    }
            else:
                pdf_path = temp_path

            # Нормализуем название файла
            normalized_filename = self.normalize_filename(original_filename)
            final_path = self.upload_folder / normalized_filename

            # Если файл с таким именем уже существует - добавляем суффикс
            counter = 1
            while final_path.exists():
                name_stem = Path(normalized_filename).stem
                final_path = self.upload_folder / f"{name_stem}_{counter}.pdf"
                counter += 1

            # Переименовываем в финальное имя
            pdf_path.rename(final_path)

            # Извлекаем метаданные
            code_info = self.extract_code(original_filename)
            if code_info:
                prefix, code = code_info
                title = manual_title or f"{prefix} {code}"
                category = manual_category or self.CATEGORIES.get(prefix, 'Общие')
                year = self.extract_year(code)
            else:
                title = manual_title or Path(normalized_filename).stem
                category = manual_category or 'Общие'
                year = None

            # Подсчитываем страницы
            pages = self.count_pages(final_path)

            # Загружаем в Wasabi, если storage настроен
            file_url = None
            if self.storage:
                try:
                    object_name = f"documents/{normalized_filename}"
                    file_url = self.storage.upload_file_from_path(
                        str(final_path),
                        object_name,
                        content_type='application/pdf'
                    )

                    # Удаляем локальный файл после успешной загрузки
                    if file_url:
                        final_path.unlink()
                        file_path_result = file_url
                    else:
                        file_path_result = final_path.name
                except Exception as e:
                    # Если не удалось загрузить в Wasabi - оставляем локальный файл
                    file_path_result = final_path.name
            else:
                # Без storage - используем локальный путь
                file_path_result = final_path.name

            return {
                'status': 'success',
                'file_path': file_path_result,
                'title': title,
                'category': category,
                'year': year,
                'pages': pages,
                'description': manual_description,
                'original_filename': original_filename,
                'normalized_filename': normalized_filename
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
