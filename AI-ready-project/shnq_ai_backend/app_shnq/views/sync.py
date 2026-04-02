"""
Django API endpoint для приёма документов от Flask backend
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.base import ContentFile
import requests
import logging

from ..models import Document, Category

logger = logging.getLogger(__name__)


@api_view(['POST'])
def sync_document(request):
    """
    Принимает документ от Flask backend и обрабатывает его

    POST /api/sync-document/
    {
        "document_id": 123,
        "title": "SHNQ 2.01.01-22",
        "code": "SHNQ 2.01.01-22",
        "category": "Строительство",
        "year": 2022,
        "file_path": "SHNQ_2.01.01-22.pdf",
        "file_url": "http://flask-backend:5000/uploads/documents/SHNQ_2.01.01-22.pdf",
        "pages": 45
    }
    """
    try:
        # Извлекаем данные
        document_id = request.data.get('document_id')
        title = request.data.get('title')
        code = request.data.get('code')
        category_name = request.data.get('category', 'SHNQ')
        year = request.data.get('year')
        file_path = request.data.get('file_path')
        file_url = request.data.get('file_url')
        pages = request.data.get('pages', 0)

        # Валидация
        if not all([title, code, file_path]):
            return Response(
                {'error': 'Missing required fields: title, code, file_path'},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"sync_document: {code} ({pages} pages)")

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

        # Скачиваем PDF файл (если передан file_url)
        pdf_file = None
        if file_url:
            try:
                response = requests.get(file_url, timeout=30)
                if response.status_code == 200:
                    pdf_file = ContentFile(response.content, name=file_path)
            except Exception as e:
                logger.warning(f"Failed to download PDF: {e}")

        # Создаём документ
        document = Document.objects.create(
            category=category,
            title=title,
            code=code,
        )

        # Сохраняем PDF файл
        if pdf_file:
            document.original_file.save(file_path, pdf_file, save=True)

        logger.info(f"Document {code} created successfully")

        # TODO: Запустить парсинг PDF и создание embeddings
        # Это будет фоновая задача (Celery или встроенный скрипт)
        # from ..tasks import process_document_async
        # process_document_async.delay(document.id)

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
