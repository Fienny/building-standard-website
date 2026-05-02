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

    if not doc.file_path:
        return jsonify({"error": "Файл документа не загружен"}), 404

    try:
        # Download PDF from Wasabi S3
        from app.services.storage import get_wasabi_storage
        wasabi = get_wasabi_storage()
        pdf_bytes = wasabi.download_file(doc.file_path)

        # Create preview from downloaded PDF
        from io import BytesIO
        import fitz  # PyMuPDF

        # Open PDF from bytes
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")

        # Create new PDF with only first 2 pages
        preview_pdf = fitz.open()
        max_pages = min(2, pdf.page_count)
        preview_pdf.insert_pdf(pdf, from_page=0, to_page=max_pages - 1)

        # Convert to bytes
        preview_bytes = preview_pdf.tobytes()

        # Close PDFs
        pdf.close()
        preview_pdf.close()

        return send_file(
            BytesIO(preview_bytes),
            mimetype="application/pdf",
            download_name=f"preview_{doc_id}.pdf",
        )

    except Exception as e:
        current_app.logger.error(f"Preview error for doc {doc_id}: {str(e)}")
        return jsonify({"error": "Не удалось создать превью"}), 500


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

    if not doc.file_path:
        return jsonify({"error": "Файл документа не загружен"}), 404

    try:
        # Download full PDF from Wasabi S3
        from app.services.storage import get_wasabi_storage
        from io import BytesIO

        wasabi = get_wasabi_storage()
        pdf_bytes = wasabi.download_file(doc.file_path)

        # Extract filename from path
        filename = os.path.basename(doc.file_path)

        return send_file(
            BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        current_app.logger.error(f"Download error for doc {doc_id}: {str(e)}")
        return jsonify({"error": "Не удалось скачать файл"}), 500
