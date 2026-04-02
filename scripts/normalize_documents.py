#!/usr/bin/env python3
"""
Скрипт нормализации названий документов SHNQ/КМҚ/КР
Конвертирует DOC/DOCX в PDF и создаёт единую структуру
"""
import os
import re
import csv
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple


class DocumentNormalizer:
    """Нормализация документов SHNQ"""

    # Паттерны для извлечения кода документа
    PATTERNS = [
        # SHNQ 1.02.10-23
        r'SHNQ[\s_-]+(\d+\.\d+\.\d+[-_]\d+)',
        r'shnq[\s_-]+(\d+\.\d+\.\d+[-_]\d+)',

        # КМҚ / кмк
        r'[KkКк][MmМм][QqҚқ][\s_-]+(\d+\.\d+\.\d+[-_]\d+)',

        # КР
        r'[KkКк][RrРр][\s_-]+(\d+\.\d+[-_]\d+)',

        # shnk-1.02.07-19 (старый формат)
        r'shnk[-_](\d+\.\d+\.\d+[-_]\d+)',

        # 2.01.04-18 (только номер)
        r'^(\d+\.\d+\.\d+[-_]\d+)',
    ]

    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.normalized_dir = self.output_dir / "normalized"
        self.original_backup = self.output_dir / "original"

        # Создаём папки
        self.normalized_dir.mkdir(parents=True, exist_ok=True)
        self.original_backup.mkdir(parents=True, exist_ok=True)

        self.metadata = []

    def extract_code(self, filename: str) -> Optional[Tuple[str, str]]:
        """
        Извлекает код документа из названия файла
        Returns: (prefix, code) или None
        """
        filename_lower = filename.lower()

        for pattern in self.PATTERNS:
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
                    prefix = 'SHNQ'  # По умолчанию

                return prefix, code

        return None

    def detect_language(self, filename: str) -> str:
        """Определяет язык документа по названию"""
        filename_lower = filename.lower()

        if any(x in filename_lower for x in ['uzbek', 'uzb', 'uz']):
            if any(x in filename_lower for x in ['rus', 'ru', 'russian']):
                return 'uz+ru'
            return 'uz'
        elif any(x in filename_lower for x in ['rus', 'ru', 'russian']):
            return 'ru'

        return 'unknown'

    def convert_doc_to_pdf(self, doc_path: Path) -> Optional[Path]:
        """Конвертирует DOC/DOCX в PDF через LibreOffice"""
        try:
            output_dir = doc_path.parent

            # Команда LibreOffice для конвертации
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
                    return pdf_path

            print(f"❌ Ошибка конвертации {doc_path.name}: {result.stderr}")
            return None

        except Exception as e:
            print(f"❌ Ошибка конвертации {doc_path.name}: {e}")
            return None

    def normalize_file(self, file_path: Path) -> Dict:
        """Нормализует один файл"""
        original_name = file_path.name
        file_ext = file_path.suffix.lower()

        # Извлекаем код документа
        code_info = self.extract_code(original_name)
        if not code_info:
            return {
                'original_name': original_name,
                'status': 'error',
                'message': 'Не удалось извлечь код документа'
            }

        prefix, code = code_info
        normalized_name = f"{prefix}_{code}.pdf"

        # Резервная копия оригинала
        backup_path = self.original_backup / original_name
        shutil.copy2(file_path, backup_path)

        # Конвертация DOC/DOCX → PDF
        source_pdf = file_path
        converted = False

        if file_ext in ['.doc', '.docx']:
            print(f"📄 Конвертирую {original_name}...")
            converted_pdf = self.convert_doc_to_pdf(file_path)

            if converted_pdf:
                source_pdf = converted_pdf
                converted = True
            else:
                return {
                    'original_name': original_name,
                    'status': 'error',
                    'message': 'Ошибка конвертации DOC/DOCX'
                }

        # Копируем в normalized с новым именем
        dest_path = self.normalized_dir / normalized_name
        shutil.copy2(source_pdf, dest_path)

        # Удаляем временный PDF после конвертации
        if converted and source_pdf.exists():
            source_pdf.unlink()

        # Метаданные
        language = self.detect_language(original_name)
        year = code.split('-')[-1] if '-' in code else 'unknown'
        size_kb = file_path.stat().st_size // 1024

        return {
            'original_name': original_name,
            'normalized_name': normalized_name,
            'code': f"{prefix} {code}",
            'year': year,
            'language': language,
            'format': file_ext[1:],
            'size_kb': size_kb,
            'status': 'converted' if converted else 'ok',
            'message': ''
        }

    def process_all(self):
        """Обрабатывает все файлы в папке"""
        print(f"📂 Сканирую: {self.input_dir}")

        # Находим все PDF и DOC/DOCX
        files = list(self.input_dir.glob('*.pdf'))
        files += list(self.input_dir.glob('*.doc'))
        files += list(self.input_dir.glob('*.docx'))

        print(f"📊 Найдено файлов: {len(files)}")

        for file_path in sorted(files):
            print(f"\n🔄 Обработка: {file_path.name}")
            result = self.normalize_file(file_path)
            self.metadata.append(result)

            if result['status'] == 'ok':
                print(f"✅ {result['normalized_name']}")
            elif result['status'] == 'converted':
                print(f"✅ Конвертировано → {result['normalized_name']}")
            else:
                print(f"❌ {result['message']}")

        # Сохраняем метаданные
        self.save_metadata()
        self.print_summary()

    def save_metadata(self):
        """Сохраняет метаданные в CSV"""
        csv_path = self.output_dir / 'metadata.csv'

        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            if self.metadata:
                writer = csv.DictWriter(f, fieldnames=self.metadata[0].keys())
                writer.writeheader()
                writer.writerows(self.metadata)

        print(f"\n💾 Метаданные сохранены: {csv_path}")

    def print_summary(self):
        """Печатает сводку"""
        total = len(self.metadata)
        ok = sum(1 for m in self.metadata if m['status'] == 'ok')
        converted = sum(1 for m in self.metadata if m['status'] == 'converted')
        errors = sum(1 for m in self.metadata if m['status'] == 'error')

        print("\n" + "="*50)
        print("📊 СВОДКА")
        print("="*50)
        print(f"Всего файлов:      {total}")
        print(f"✅ Обработано:     {ok}")
        print(f"📄 Конвертировано: {converted}")
        print(f"❌ Ошибок:         {errors}")
        print("="*50)


def main():
    import sys

    if len(sys.argv) < 2:
        print("Использование: python normalize_documents.py <папка_с_документами>")
        print("Пример: python normalize_documents.py ./documents-archive/UMUMIY")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./documents-normalized"

    normalizer = DocumentNormalizer(input_dir, output_dir)
    normalizer.process_all()


if __name__ == "__main__":
    main()
