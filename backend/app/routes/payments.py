from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.document import Document
from app.models.purchase import Purchase
from app.models.payment import Payment

payments_bp = Blueprint("payments", __name__)


@payments_bp.route("/create", methods=["POST"])
@jwt_required()
def create_payment():
    """Create a new purchase + payment record."""
    uid = int(get_jwt_identity())
    data = request.get_json() or {}

    document_id = data.get("document_id")
    payment_method = data.get("payment_method")

    if not document_id or not payment_method:
        return jsonify({"error": "document_id и payment_method обязательны"}), 400

    if payment_method not in ("click", "payme", "card"):
        return jsonify({"error": "Неверный метод оплаты"}), 400

    doc = Document.query.get(document_id)
    if not doc or not doc.is_active:
        return jsonify({"error": "Документ не найден"}), 404

    # Check for existing completed purchase
    existing = Purchase.query.filter_by(
        user_id=uid, document_id=document_id, payment_status="completed"
    ).first()
    if existing:
        return jsonify({"error": "Вы уже приобрели этот документ"}), 400

    purchase = Purchase(
        user_id=uid,
        document_id=document_id,
        amount=doc.price,
        payment_method=payment_method,
        payment_status="pending",
    )
    db.session.add(purchase)
    db.session.flush()

    payment = Payment(
        purchase_id=purchase.id,
        payment_system=payment_method,
        amount=doc.price,
        status="pending",
    )
    db.session.add(payment)
    db.session.commit()

    # TODO: When payment APIs are integrated, create a real transaction here
    # and populate payment.payment_url / transaction_id.

    return jsonify({
        "message": "Платеж создан",
        "purchase_id": purchase.id,
        "payment_id": payment.id,
        "amount": doc.price,
    }), 201


@payments_bp.route("/callback/<system>", methods=["POST"])
def payment_callback(system):
    """Webhook endpoint for payment systems (Click, PayMe, card)."""
    data = request.get_json() or {}

    # TODO: Validate signature from the payment system
    # TODO: Update purchase.payment_status and payment.status accordingly

    return jsonify({"success": True})


@payments_bp.route("/status/<int:payment_id>", methods=["GET"])
@jwt_required()
def payment_status(payment_id):
    uid = int(get_jwt_identity())

    payment = Payment.query.get_or_404(payment_id)
    purchase = Purchase.query.get(payment.purchase_id)

    if not purchase or purchase.user_id != uid:
        return jsonify({"error": "Платеж не найден"}), 404

    return jsonify({
        "payment_id": payment.id,
        "status": payment.status,
        "amount": payment.amount,
        "payment_system": payment.payment_system,
    })


@payments_bp.route("/history", methods=["GET"])
@jwt_required()
def payment_history():
    uid = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)

    pagination = (
        Purchase.query.filter_by(user_id=uid)
        .order_by(Purchase.created_at.desc())
        .paginate(page=page, per_page=limit, error_out=False)
    )

    results = []
    for p in pagination.items:
        doc = Document.query.get(p.document_id)
        results.append({
            **p.to_dict(),
            "document": doc.to_dict() if doc else None,
        })

    return jsonify({
        "purchases": results,
        "pagination": {
            "total": pagination.total,
            "page": page,
            "limit": limit,
            "totalPages": pagination.pages,
        },
    })
