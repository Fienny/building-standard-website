from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.document import Document
from app.models.purchase import Purchase
from app.models.payment import Payment
from app.services.click_service import ClickService
from app.services.payme_service import PaymeService
from app.services.card_service import CardService

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

    # Generate return URL
    frontend_url = current_app.config.get("FRONTEND_URL", "http://localhost:5173")
    return_url = f"{frontend_url}/payment/success?purchase_id={purchase.id}"
    fail_url = f"{frontend_url}/payment/failed?purchase_id={purchase.id}"

    # Prepare payment with appropriate service
    payment_data = None
    try:
        if payment_method == "click":
            payment_data = ClickService.prepare_payment(
                amount=doc.price,
                merchant_trans_id=f"purchase_{purchase.id}",
                return_url=return_url,
                description=f"Покупка документа: {doc.title}",
            )
        elif payment_method == "payme":
            payment_data = PaymeService.prepare_payment(
                amount=doc.price,
                account_id=str(purchase.id),
                description=f"Покупка документа: {doc.title}",
                return_url=return_url,
            )
        elif payment_method == "card":
            payment_data = CardService.prepare_payment(
                amount=doc.price,
                order_id=f"purchase_{purchase.id}",
                description=f"Покупка документа: {doc.title}",
                return_url=return_url,
                fail_url=fail_url,
            )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Ошибка создания платежа: {str(e)}"}), 500

    if not payment_data:
        db.session.rollback()
        return jsonify({"error": "Не удалось создать платеж"}), 500

    # Create payment record
    payment = Payment(
        purchase_id=purchase.id,
        payment_system=payment_method,
        amount=doc.price,
        status="pending",
        payment_url=payment_data.get("payment_url"),
        transaction_id=payment_data.get("transaction_id"),
    )
    db.session.add(payment)
    db.session.commit()

    return jsonify({
        "message": "Платеж создан",
        "purchase_id": purchase.id,
        "payment_id": payment.id,
        "amount": doc.price,
        "payment_url": payment_data.get("payment_url"),
    }), 201


@payments_bp.route("/callback/click", methods=["POST"])
def click_callback():
    """Webhook endpoint for Click payment system."""
    data = request.form.to_dict()  # Click sends form data

    # Verify callback
    result = ClickService.verify_callback(data)

    if result.get("error"):
        return jsonify(result), 400

    # Extract data
    merchant_trans_id = result.get("merchant_trans_id")
    click_trans_id = result.get("click_trans_id")
    action = result.get("action")  # 0 = prepare, 1 = complete

    # Get purchase
    purchase_id = merchant_trans_id.replace("purchase_", "")
    purchase = Purchase.query.get(purchase_id)

    if not purchase:
        return jsonify({"error": -5, "error_note": "Purchase not found"}), 404

    # Get payment
    payment = Payment.query.filter_by(purchase_id=purchase.id).first()

    if action == 0:
        # Prepare action - just verify
        return jsonify({
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_prepare_id": payment.id if payment else None,
            "error": 0,
            "error_note": "Success",
        })
    elif action == 1:
        # Complete action - mark as paid
        if payment:
            payment.status = "completed"
            payment.transaction_id = click_trans_id
            payment.callback_data = data

        purchase.payment_status = "completed"
        purchase.transaction_id = click_trans_id

        db.session.commit()

        return jsonify({
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_confirm_id": payment.id if payment else None,
            "error": 0,
            "error_note": "Success",
        })

    return jsonify({"error": -1, "error_note": "Invalid action"}), 400


@payments_bp.route("/callback/payme", methods=["POST"])
def payme_callback():
    """Webhook endpoint for PayMe payment system (JSON-RPC)."""
    data = request.get_json() or {}

    method = data.get("method")
    params = data.get("params", {})
    request_id = data.get("id")

    # Handle different RPC methods
    if method == "CheckPerformTransaction":
        account = params.get("account", {})
        purchase_id = account.get("purchase_id")
        amount = params.get("amount")

        purchase = Purchase.query.get(purchase_id)
        if not purchase:
            return jsonify({
                "error": {
                    "code": PaymeService.ERROR_INVALID_ACCOUNT,
                    "message": "Purchase not found",
                },
                "id": request_id,
            })

        # Check amount (PayMe sends in tiyin)
        expected_amount = purchase.amount * 100
        if amount != expected_amount:
            return jsonify({
                "error": {
                    "code": PaymeService.ERROR_INVALID_AMOUNT,
                    "message": "Invalid amount",
                },
                "id": request_id,
            })

        return jsonify({
            "result": {"allow": True},
            "id": request_id,
        })

    elif method == "CreateTransaction":
        payme_trans_id = params.get("id")
        account = params.get("account", {})
        purchase_id = account.get("purchase_id")
        amount = params.get("amount")
        time_ms = params.get("time")

        purchase = Purchase.query.get(purchase_id)
        if not purchase:
            return jsonify({
                "error": {
                    "code": PaymeService.ERROR_INVALID_ACCOUNT,
                    "message": "Purchase not found",
                },
                "id": request_id,
            })

        # Create or get payment
        payment = Payment.query.filter_by(purchase_id=purchase.id).first()
        if not payment:
            payment = Payment(
                purchase_id=purchase.id,
                payment_system="payme",
                amount=purchase.amount,
                status="pending",
                transaction_id=payme_trans_id,
            )
            db.session.add(payment)

        payment.callback_data = {"state": PaymeService.STATE_CREATED, "time": time_ms}
        db.session.commit()

        return jsonify({
            "result": {
                "create_time": time_ms,
                "transaction": str(payment.id),
                "state": PaymeService.STATE_CREATED,
            },
            "id": request_id,
        })

    elif method == "PerformTransaction":
        payme_trans_id = params.get("id")

        # Find payment by PayMe transaction ID
        payment = Payment.query.filter_by(transaction_id=payme_trans_id).first()
        if not payment:
            return jsonify({
                "error": {
                    "code": PaymeService.ERROR_TRANSACTION_NOT_FOUND,
                    "message": "Transaction not found",
                },
                "id": request_id,
            })

        # Complete payment
        payment.status = "completed"
        payment.callback_data["state"] = PaymeService.STATE_COMPLETED

        purchase = Purchase.query.get(payment.purchase_id)
        purchase.payment_status = "completed"

        db.session.commit()

        return jsonify({
            "result": {
                "transaction": str(payment.id),
                "perform_time": payment.callback_data.get("time"),
                "state": PaymeService.STATE_COMPLETED,
            },
            "id": request_id,
        })

    elif method == "CancelTransaction":
        payme_trans_id = params.get("id")
        reason = params.get("reason")

        payment = Payment.query.filter_by(transaction_id=payme_trans_id).first()
        if not payment:
            return jsonify({
                "error": {
                    "code": PaymeService.ERROR_TRANSACTION_NOT_FOUND,
                    "message": "Transaction not found",
                },
                "id": request_id,
            })

        payment.status = "cancelled"
        payment.callback_data["state"] = PaymeService.STATE_CANCELLED
        payment.callback_data["reason"] = reason

        purchase = Purchase.query.get(payment.purchase_id)
        purchase.payment_status = "cancelled"

        db.session.commit()

        return jsonify({
            "result": {
                "transaction": str(payment.id),
                "cancel_time": int(payment.callback_data.get("time", 0)),
                "state": PaymeService.STATE_CANCELLED,
            },
            "id": request_id,
        })

    elif method == "CheckTransaction":
        payme_trans_id = params.get("id")

        payment = Payment.query.filter_by(transaction_id=payme_trans_id).first()
        if not payment:
            return jsonify({
                "error": {
                    "code": PaymeService.ERROR_TRANSACTION_NOT_FOUND,
                    "message": "Transaction not found",
                },
                "id": request_id,
            })

        state = payment.callback_data.get("state", PaymeService.STATE_CREATED)

        return jsonify({
            "result": {
                "create_time": payment.callback_data.get("time"),
                "transaction": str(payment.id),
                "state": state,
            },
            "id": request_id,
        })

    return jsonify({
        "error": {
            "code": -32601,
            "message": "Method not found",
        },
        "id": request_id,
    })


@payments_bp.route("/callback/card", methods=["POST"])
def card_callback():
    """Webhook endpoint for card payment system."""
    data = request.get_json() or {}

    # Verify callback
    result = CardService.verify_callback(data)

    if not result.get("valid"):
        return jsonify({"success": False, "error": result.get("error")}), 400

    # Extract data
    order_id = result.get("order_id")
    transaction_id = result.get("transaction_id")
    status = result.get("status")

    # Get purchase
    purchase_id = order_id.replace("purchase_", "")
    purchase = Purchase.query.get(purchase_id)

    if not purchase:
        return jsonify({"success": False, "error": "Purchase not found"}), 404

    # Get payment
    payment = Payment.query.filter_by(purchase_id=purchase.id).first()

    if status == "success":
        if payment:
            payment.status = "completed"
            payment.transaction_id = transaction_id
            payment.callback_data = data

        purchase.payment_status = "completed"
        purchase.transaction_id = transaction_id

    elif status == "failed":
        if payment:
            payment.status = "failed"
            payment.callback_data = data

        purchase.payment_status = "failed"

    db.session.commit()

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
