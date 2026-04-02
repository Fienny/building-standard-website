"""
Синхронизация документов с Django AI backend
"""
import requests
from typing import Dict
from pathlib import Path


class AIBackendSync:
    """Синхронизация с AI backend"""

    def __init__(self, ai_backend_url: str):
        self.ai_backend_url = ai_backend_url.rstrip('/')
        self.timeout = 120  # 2 минуты на обработку PDF

    def sync_document(self, document) -> Dict:
        """
        Отправляет документ в AI backend для обработки
        """
        try:
            # Формируем данные для отправки
            data = {
                'document_id': document.id,
                'title': document.title,
                'code': self._extract_code_from_title(document.title),
                'category': document.category,
                'year': document.year,
                'file_path': document.file_path,
                'pages': document.pages,
            }

            # Отправляем POST запрос в AI backend
            response = requests.post(
                f"{self.ai_backend_url}/api/sync-document/",
                json=data,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return {
                    'status': 'success',
                    'message': 'Документ успешно синхронизирован с AI backend'
                }
            else:
                return {
                    'status': 'error',
                    'message': f"AI backend вернул ошибку: {response.status_code}"
                }

        except requests.ConnectionError:
            return {
                'status': 'error',
                'message': 'AI backend недоступен. Проверьте что Django сервер запущен.'
            }
        except requests.Timeout:
            return {
                'status': 'error',
                'message': 'Timeout при обработке документа (>2 мин). Документ слишком большой?'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Ошибка синхронизации: {str(e)}'
            }

    def delete_document(self, document) -> Dict:
        """
        Удаляет документ из AI backend
        """
        try:
            code = self._extract_code_from_title(document.title)

            response = requests.delete(
                f"{self.ai_backend_url}/api/documents/{code}/",
                timeout=30
            )

            if response.status_code in [200, 204]:
                return {
                    'status': 'success',
                    'message': 'Документ удалён из AI backend'
                }
            else:
                return {
                    'status': 'error',
                    'message': f"Ошибка удаления: {response.status_code}"
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def _extract_code_from_title(self, title: str) -> str:
        """
        Извлекает код документа из заголовка
        Example: "SHNQ 2.01.01-22" → "SHNQ 2.01.01-22"
        """
        # Простое извлечение первых слов (обычно это и есть код)
        parts = title.split()
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1]}"
        return title
