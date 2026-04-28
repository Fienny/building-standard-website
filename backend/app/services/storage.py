"""
S3/Wasabi Storage Service для загрузки и хранения документов
"""
import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
import logging

logger = logging.getLogger(__name__)


class WasabiStorage:
    """Сервис для работы с Wasabi S3-compatible storage"""

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        region: str = 'eu-central-1'
    ):
        self.bucket_name = bucket_name
        self.region = region

        # Wasabi endpoint для региона
        self.endpoint_url = f'https://s3.{region}.wasabisys.com'

        # Инициализация S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=self.endpoint_url,
            region_name=region
        )

        logger.info(f"Wasabi storage initialized: bucket={bucket_name}, region={region}")

    def upload_file(
        self,
        file_obj: BinaryIO,
        object_name: str,
        content_type: str = 'application/pdf'
    ) -> Optional[str]:
        """
        Загружает файл в Wasabi bucket

        Args:
            file_obj: Файловый объект для загрузки
            object_name: Имя файла в bucket (например: documents/SHNQ_2.01.01-22.pdf)
            content_type: MIME тип файла

        Returns:
            URL файла или None при ошибке
        """
        try:
            # Загружаем файл
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                object_name,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'public-read'  # Публичный доступ для чтения
                }
            )

            # Формируем публичный URL
            file_url = f"{self.endpoint_url}/{self.bucket_name}/{object_name}"

            logger.info(f"File uploaded to Wasabi: {object_name}")
            return file_url

        except ClientError as e:
            logger.error(f"Wasabi upload error: {str(e)}")
            return None

    def upload_file_from_path(
        self,
        file_path: str,
        object_name: str,
        content_type: str = 'application/pdf'
    ) -> Optional[str]:
        """
        Загружает файл из локального пути в Wasabi

        Args:
            file_path: Путь к локальному файлу
            object_name: Имя файла в bucket
            content_type: MIME тип файла

        Returns:
            URL файла или None при ошибке
        """
        try:
            with open(file_path, 'rb') as f:
                return self.upload_file(f, object_name, content_type)
        except Exception as e:
            logger.error(f"File upload from path error: {str(e)}")
            return None

    def delete_file(self, object_name: str) -> bool:
        """
        Удаляет файл из Wasabi bucket

        Args:
            object_name: Имя файла в bucket

        Returns:
            True если успешно, False при ошибке
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_name
            )
            logger.info(f"File deleted from Wasabi: {object_name}")
            return True

        except ClientError as e:
            logger.error(f"Wasabi delete error: {str(e)}")
            return False

    def file_exists(self, object_name: str) -> bool:
        """
        Проверяет существование файла в bucket

        Args:
            object_name: Имя файла в bucket

        Returns:
            True если файл существует, False если нет
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=object_name
            )
            return True
        except ClientError:
            return False

    def get_file_url(self, object_name: str) -> str:
        """
        Возвращает публичный URL файла

        Args:
            object_name: Имя файла в bucket

        Returns:
            Публичный URL файла
        """
        return f"{self.endpoint_url}/{self.bucket_name}/{object_name}"

    def list_files(self, prefix: str = '') -> list:
        """
        Список файлов в bucket

        Args:
            prefix: Префикс для фильтрации (например: 'documents/')

        Returns:
            Список имён файлов
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )

            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []

        except ClientError as e:
            logger.error(f"Wasabi list error: {str(e)}")
            return []


def get_wasabi_storage() -> WasabiStorage:
    """
    Фабрика для создания Wasabi storage instance из переменных окружения
    """
    return WasabiStorage(
        access_key=os.getenv('WASABI_ACCESS_KEY_ID'),
        secret_key=os.getenv('WASABI_SECRET_ACCESS_KEY'),
        bucket_name=os.getenv('WASABI_BUCKET_NAME', 'standards'),
        region=os.getenv('WASABI_REGION', 'eu-central-1')
    )
