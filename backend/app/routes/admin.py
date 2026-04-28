"""
Admin panel routes для управления документами
"""
import os
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app import db
from app.models.document import Document
from app.models.user import User
from app.services.document_processor import DocumentProcessor
from app.services.ai_sync import AIBackendSync
from app.services.storage import get_wasabi_storage

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required():
    """Проверка прав администратора"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        flash('Доступ запрещён. Требуются права администратора.', 'error')
        return False
    return True


@admin_bp.route('/documents')
@jwt_required()
def list_documents():
    """Список всех документов"""
    if not admin_required():
        return redirect(url_for('auth.login'))

    # Пагинация
    page = request.args.get('page', 1, type=int)
    per_page = 20

    documents = Document.query.order_by(Document.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('admin/documents.html', documents=documents)


@admin_bp.route('/documents/new', methods=['GET', 'POST'])
@jwt_required()
def new_document():
    """Создание нового документа с автоматической обработкой"""
    if not admin_required():
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        # Получаем файл
        if 'file' not in request.files:
            flash('Файл не выбран', 'error')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('Файл не выбран', 'error')
            return redirect(request.url)

        # Получаем метаданные из формы (опционально)
        manual_title = request.form.get('title', '').strip()
        manual_category = request.form.get('category', '').strip()
        manual_description = request.form.get('description', '').strip()
        auto_sync_ai = request.form.get('sync_ai', 'on') == 'on'

        try:
            # Инициализируем процессор документов с Wasabi storage
            storage = get_wasabi_storage()
            processor = DocumentProcessor(current_app.config['UPLOAD_FOLDER'], storage=storage)

            # Обрабатываем файл (автоматически)
            result = processor.process_upload(
                file,
                manual_title=manual_title,
                manual_category=manual_category,
                manual_description=manual_description
            )

            if result['status'] == 'error':
                flash(f"Ошибка обработки: {result['message']}", 'error')
                return redirect(request.url)

            # Создаём запись в БД
            document = Document(
                title=result['title'],
                category=result['category'],
                year=result['year'],
                pages=result['pages'],
                description=result['description'] or manual_description,
                file_path=result['file_path'],
                is_active=True
            )

            db.session.add(document)
            db.session.commit()

            flash(f"✅ Документ '{result['title']}' успешно добавлен ({result['pages']} стр.)", 'success')

            # Автоматическая синхронизация с AI backend
            if auto_sync_ai:
                try:
                    ai_sync = AIBackendSync(current_app.config['AI_BACKEND_URL'])
                    sync_result = ai_sync.sync_document(document)

                    if sync_result['status'] == 'success':
                        flash(f"🤖 AI backend синхронизирован", 'success')
                    else:
                        flash(f"⚠️ AI синхронизация не удалась: {sync_result.get('message')}", 'warning')
                except Exception as e:
                    flash(f"⚠️ AI синхронизация не удалась: {str(e)}", 'warning')

            return redirect(url_for('admin.list_documents'))

        except Exception as e:
            flash(f"Ошибка: {str(e)}", 'error')
            return redirect(request.url)

    return render_template('admin/new_document.html')


@admin_bp.route('/documents/<int:doc_id>/edit', methods=['GET', 'POST'])
@jwt_required()
def edit_document(doc_id):
    """Редактирование документа"""
    if not admin_required():
        return redirect(url_for('auth.login'))

    document = Document.query.get_or_404(doc_id)

    if request.method == 'POST':
        document.title = request.form.get('title', document.title)
        document.category = request.form.get('category', document.category)
        document.year = request.form.get('year', document.year, type=int)
        document.description = request.form.get('description', document.description)
        document.is_active = request.form.get('is_active', 'off') == 'on'

        db.session.commit()
        flash(f"✅ Документ обновлён", 'success')

        return redirect(url_for('admin.list_documents'))

    return render_template('admin/edit_document.html', document=document)


@admin_bp.route('/documents/<int:doc_id>/delete', methods=['POST'])
@jwt_required()
def delete_document(doc_id):
    """Удаление документа"""
    if not admin_required():
        return redirect(url_for('auth.login'))

    document = Document.query.get_or_404(doc_id)

    # Удаляем файл из Wasabi или локальной файловой системы
    if document.file_path:
        if document.file_path.startswith('http'):
            # Файл в Wasabi - удаляем через storage API
            try:
                storage = get_wasabi_storage()
                # Извлекаем object_name из URL
                # URL формата: https://s3.eu-central-1.wasabisys.com/standards/documents/SHNQ_X.XX.XX-YY.pdf
                object_name = '/'.join(document.file_path.split('/')[-2:])  # documents/SHNQ_X.XX.XX-YY.pdf
                storage.delete_file(object_name)
            except Exception as e:
                flash(f"⚠️ Не удалось удалить файл из Wasabi: {str(e)}", 'warning')
        else:
            # Локальный файл - удаляем из файловой системы
            file_path = Path(current_app.config['UPLOAD_FOLDER']) / document.file_path
            if file_path.exists():
                file_path.unlink()

    # Удаляем из AI backend
    try:
        ai_sync = AIBackendSync(current_app.config['AI_BACKEND_URL'])
        ai_sync.delete_document(document)
    except Exception as e:
        flash(f"⚠️ Не удалось удалить из AI backend: {str(e)}", 'warning')

    # Удаляем из БД
    db.session.delete(document)
    db.session.commit()

    flash(f"✅ Документ '{document.title}' удалён", 'success')
    return redirect(url_for('admin.list_documents'))


@admin_bp.route('/documents/<int:doc_id>/sync-ai', methods=['POST'])
@jwt_required()
def sync_ai(doc_id):
    """Ручная синхронизация с AI backend"""
    if not admin_required():
        return redirect(url_for('auth.login'))

    document = Document.query.get_or_404(doc_id)

    try:
        ai_sync = AIBackendSync(current_app.config['AI_BACKEND_URL'])
        result = ai_sync.sync_document(document)

        if result['status'] == 'success':
            flash(f"✅ AI backend синхронизирован", 'success')
        else:
            flash(f"❌ Ошибка синхронизации: {result.get('message')}", 'error')

    except Exception as e:
        flash(f"❌ Ошибка: {str(e)}", 'error')

    return redirect(url_for('admin.list_documents'))
