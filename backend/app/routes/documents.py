import os

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

from app import db
from app.models.document import Document
from app.models.purchase import Purchase
from app.services.file_service import get_preview_pdf

documents_bp = Blueprint("documents", __name__)


@documents_bp.route("", methods=["GET"])
def list_documents():
    """Get paginated list of documents with optional search/category filter."""
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "all")
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 50, type=int)

    query = Document.query.filter_by(is_active=True)

    if category and category != "all":
        query = query.filter_by(category=category)

    if search:
        query = query.filter(Document.title.ilike(f"%{search}%"))

    query = query.order_by(Document.created_at.desc())
    pagination = query.paginate(page=page, per_page=limit, error_out=False)

    return jsonify({
        "documents": [d.to_dict() for d in pagination.items],
        "pagination": {
            "total": pagination.total,
            "page": page,
            "limit": limit,
            "totalPages": pagination.pages,
        },
    })


@documents_bp.route("/categories", methods=["GET"])
def list_categories():
    """Get all unique categories."""
    rows = (
        db.session.query(Document.category)
        .filter_by(is_active=True)
        .distinct()
        .order_by(Document.category)
        .all()
    )
    return jsonify({"categories": [r[0] for r in rows]})


@documents_bp.route("/<int:doc_id>", methods=["GET"])
def get_document(doc_id):
    """Get single document detail. If user is authenticated, also tell whether purchased."""
    doc = Document.query.get_or_404(doc_id)
    if not doc.is_active:
        return jsonify({"error": "Документ недоступен"}), 404

    is_purchased = False
    try:
        verify_jwt_in_request(optional=True)
        uid = get_jwt_identity()
        if uid:
            is_purchased = (
                Purchase.query.filter_by(
                    user_id=int(uid),
                    document_id=doc_id,
                    payment_status="completed",
                ).first()
                is not None
            )
    except Exception:
        pass

    return jsonify({"document": doc.to_dict(), "isPurchased": is_purchased})


@documents_bp.route("/<int:doc_id>/preview", methods=["GET"])
def preview_document(doc_id):
    """Return a PDF containing only the first 2 pages of the document."""
    doc = Document.query.get_or_404(doc_id)

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    if not doc.file_path:
        return jsonify({"error": "Файл документа не загружен"}), 404

    full_path = os.path.join(upload_folder, doc.file_path)
    if not os.path.isfile(full_path):
        return jsonify({"error": "Файл не найден на сервере"}), 404

    preview_bytes = get_preview_pdf(full_path, max_pages=2)
    if preview_bytes is None:
        return jsonify({"error": "Не удалось создать превью"}), 500

    from io import BytesIO

    return send_file(
        BytesIO(preview_bytes),
        mimetype="application/pdf",
        download_name=f"preview_{doc_id}.pdf",
    )


@documents_bp.route("/<int:doc_id>/download", methods=["GET"])
@jwt_required()
def download_document(doc_id):
    """Download the full document. Requires completed purchase."""
    uid = int(get_jwt_identity())
    doc = Document.query.get_or_404(doc_id)

    purchase = Purchase.query.filter_by(
        user_id=uid, document_id=doc_id, payment_status="completed"
    ).first()

    from app.models.user import User

    user = User.query.get(uid)
    if not purchase and (not user or user.role != "admin"):
        return jsonify({"error": "Документ не оплачен"}), 403

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    if not doc.file_path:
        return jsonify({"error": "Файл документа не загружен"}), 404

    full_path = os.path.join(upload_folder, doc.file_path)
    if not os.path.isfile(full_path):
        return jsonify({"error": "Файл не найден на сервере"}), 404

    return send_file(full_path, as_attachment=True)
