# Нормализация документов SHNQ

## Что делает скрипт:

1. ✅ Извлекает код документа (SHNQ 2.01.01-22)
2. ✅ Конвертирует DOC/DOCX → PDF
3. ✅ Переименовывает в единый формат: `SHNQ_2.01.01-22.pdf`
4. ✅ Создаёт резервные копии оригиналов
5. ✅ Генерирует CSV с метаданными

## Требования:

### Windows:
```powershell
# 1. Установи LibreOffice (для конвертации DOC/DOCX)
# Скачай: https://www.libreoffice.org/download/download/
# При установке добавь в PATH

# 2. Python 3.12+ уже установлен
```

### Linux/Mac:
```bash
# Установи LibreOffice
sudo apt install libreoffice  # Ubuntu/Debian
brew install libreoffice      # Mac
```

## Использование:

### Шаг 1: Подготовь файлы
```powershell
# Скачай архив UMUMIY.zip с Google Drive
# Распакуй в папку проекта
cd D:\benkas_projects\building-standard-website
mkdir documents-archive
# Распакуй UMUMIY.zip → documents-archive\UMUMIY\
```

### Шаг 2: Запусти скрипт
```powershell
cd scripts

# Windows:
python normalize_documents.py ..\documents-archive\UMUMIY

# Или укажи папку вывода:
python normalize_documents.py ..\documents-archive\UMUMIY ..\documents-normalized
```

## Результат:

```
documents-normalized/
├── original/              # Резервные копии оригиналов
│   ├── shnk-1.02.07-19-uzb.rus.pdf
│   ├── SHNQ 1.02.10-23.doc
│   └── ...
├── normalized/            # Нормализованные PDF
│   ├── SHNQ_1.02.07-19.pdf
│   ├── SHNQ_1.02.10-23.pdf
│   ├── KMQ_1.03.04-22.pdf
│   └── ...
├── metadata.csv          # Таблица с метаданными
└── conversion_log.txt    # Лог (если есть)
```

## Метаданные (metadata.csv):

```csv
original_name,normalized_name,code,year,language,format,size_kb,status,message
"shnk-1.02.07-19-uzb.rus.pdf","SHNQ_1.02.07-19.pdf","SHNQ 1.02.07-19","19","uz+ru","pdf",2282,"ok",""
"SHNQ 1.02.10-23.doc","SHNQ_1.02.10-23.pdf","SHNQ 1.02.10-23","23","uz","doc",42,"converted",""
"КМҚ 1.03.04-22    ЯНГИ.pdf","KMQ_1.03.04-22.pdf","КМҚ 1.03.04-22","22","uz","pdf",871,"ok",""
```

## Поддерживаемые форматы:

### Префиксы документов:
- `SHNQ` / `shnq` / `shnk` → `SHNQ_X.XX.XX-YY.pdf`
- `КМҚ` / `кмк` / `KMQ` / `kmq` → `KMQ_X.XX.XX-YY.pdf`
- `КР` / `kr` / `KR` → `KR_XX.XX-YY.pdf`

### Форматы файлов:
- ✅ PDF (копируется и переименовывается)
- ✅ DOC (конвертируется в PDF)
- ✅ DOCX (конвертируется в PDF)

## Примеры преобразований:

| Оригинал | Нормализованное |
|----------|----------------|
| `shnk-1.02.07-19-uzb.rus.pdf` | `SHNQ_1.02.07-19.pdf` |
| `SHNQ 1.02.10-23.doc` | `SHNQ_1.02.10-23.pdf` |
| `КМҚ 1.03.04-22    ЯНГИ.pdf` | `KMQ_1.03.04-22.pdf` |
| `кмк 3.06.07-08 узб -ГОТОВ.pdf` | `KMQ_3.06.07-08.pdf` |
| `КР 01.01-23 Худудларни...pdf` | `KR_01.01-23.pdf` |

## Troubleshooting:

### Ошибка: LibreOffice not found
```powershell
# Добавь LibreOffice в PATH:
# 1. Найди путь установки (обычно C:\Program Files\LibreOffice\program)
# 2. Добавь в переменные окружения PATH
# 3. Перезапусти PowerShell
```

### Ошибка конвертации DOC/DOCX
```powershell
# Попробуй вручную открыть в LibreOffice и сохранить как PDF
# Затем положи PDF в папку с документами
```

### Не распознался код документа
```
# Проверь название файла в metadata.csv (status: error)
# Переименуй вручную в формат: SHNQ_X.XX.XX-YY.pdf
```

## Следующий шаг:

После нормализации:
1. Проверь `metadata.csv` - все ли файлы обработаны
2. Посмотри папку `normalized/` - все ли PDF на месте
3. Скажи мне - я создам скрипт импорта в AI backend
