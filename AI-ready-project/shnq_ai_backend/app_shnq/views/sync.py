"""
Django API endpoint для приёма документов от Flask backend
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.base import ContentFile
import requests
import logging
import fitz  # PyMuPDF
import re

from ..models import Document, Category, Clause
from ..embeddings import upsert_clause_embeddings

logger = logging.getLogger(__name__)


def parse_pdf_and_create_clauses(document):
    """
    Простой парсер PDF - извлекает текст и создает Clause записи.
    Потом автоматически создаются embeddings.
    """
    try:
        # Открываем PDF
        pdf_path = document.original_file.path
        pdf = fitz.open(pdf_path)

        clauses_created = 0

        # Простая логика: каждая страница = один Clause
        for page_num in range(min(pdf.page_count, 50)):  # Ограничим 50 страницами для начала
            page = pdf[page_num]
            text = page.get_text()

            # Пропускаем пустые страницы
            if not text.strip() or len(text.strip()) < 50:
                continue

            # Ищем номера пунктов (например "5.1", "6.2.3")
            clause_numbers = re.findall(r'\b\d+\.\d+(?:\.\d+)?\b', text[:500])
            clause_number = clause_numbers[0] if clause_numbers else f"page_{page_num+1}"

            # Создаем Clause
            Clause.objects.create(
                document=document,
                clause_number=clause_number,
                text=text[:2000]  # Ограничим длину для embeddings
            )
            clauses_created += 1

        pdf.close()

        logger.info(f"Created {clauses_created} clauses for document {document.code}")

        # AUTO-CREATE EMBEDDINGS
        if clauses_created > 0:
            result = upsert_clause_embeddings()
            logger.info(f"Embeddings created: {result}")

        return clauses_created

    except Exception as e:
        logger.error(f"Failed to parse PDF: {e}", exc_info=True)
        return 0


@api_view(['POST'])
def sync_document(request):
    """
    Принимает документ от Flask backend и обрабатывает его

    POST /api/sync-document/
    Multipart form-data:
        - file: PDF file
        - document_id: Flask document ID
        - title: Document title
        - category: Category name
        - year: Publication year
        - file_path: Original filename
    """
    try:
        # Извлекаем данные из form-data
        document_id = request.data.get('document_id')
        title = request.data.get('title')
        category_name = request.data.get('category', 'SHNQ')
        year = request.data.get('year')
        file_path = request.data.get('file_path')

        # PDF file из request.FILES
        pdf_file = request.FILES.get('file')

        # Генерируем code из file_path если не передан
        code = request.data.get('code')
        if not code and file_path:
            import os
            code = os.path.splitext(os.path.basename(file_path))[0]

        # Валидация
        if not all([title, code]):
            return Response(
                {'error': 'Missing required fields: title, code'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not pdf_file:
            return Response(
                {'error': 'PDF file is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"sync_document: {code} - {title}")

        # Проверяем дубликат
        existing = Document.objects.filter(code=code).first()
        if existing:
            logger.info(f"Document {code} already exists, skipping")
            return Response({
                'status': 'skipped',
                'message': f'Document {code} already exists'
            })

        # Получаем или создаём категорию
        category_code = code.split()[0] if ' ' in code else 'SHNQ'
        category, _ = Category.objects.get_or_create(
            code=category_code,
            defaults={'name': category_name}
        )

        # Создаём документ
        document = Document.objects.create(
            category=category,
            title=title,
            code=code,
            lex_url=f"https://lex.uz/docs/{code}"  # placeholder
        )

        # Сохраняем PDF файл
        if pdf_file:
            document.original_file.save(file_path or f"{code}.pdf", pdf_file, save=True)

        logger.info(f"Document {code} created successfully")

        # AUTO-PROCESS: Парсим PDF и создаем embeddings
        try:
            clauses_count = parse_pdf_and_create_clauses(document)
            logger.info(f"Document {code} parsed: {clauses_count} clauses with embeddings")
        except Exception as e:
            logger.error(f"Failed to parse PDF: {e}", exc_info=True)
            # Не падаем - документ уже создан

        return Response({
            'status': 'success',
            'message': f'Document {code} synced successfully',
            'document_id': str(document.id)
        })

    except Exception as e:
        logger.error(f"sync_document error: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
def delete_document(request, code):
    """
    Удаляет документ из AI backend

    DELETE /api/documents/{code}/
    """
    try:
        document = Document.objects.filter(code=code).first()

        if not document:
            return Response(
                {'error': f'Document {code} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Удаляем файл
        if document.original_file:
            document.original_file.delete()
        if document.html_file:
            document.html_file.delete()

        # Удаляем все связанные данные (embeddings, clauses, tables)
        document.delete()

        logger.info(f"Document {code} deleted successfully")

        return Response({
            'status': 'success',
            'message': f'Document {code} deleted'
        }, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        logger.error(f"delete_document error: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
