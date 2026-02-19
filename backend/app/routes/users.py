from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.user import User
from app.models.purchase import Purchase
from app.models.document import Document

users_bp = Blueprint("users", __name__)


@users_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404
    return jsonify({"user": user.to_dict()})


@users_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404

    data = request.get_json() or {}

    if "name" in data:
        user.name = data["name"].strip()

    if "email" in data:
        new_email = data["email"].strip().lower()
        if new_email != user.email:
            if User.query.filter_by(email=new_email).first():
                return jsonify({"error": "Email уже занят"}), 400
            user.email = new_email

    db.session.commit()
    return jsonify({"message": "Профиль обновлен", "user": user.to_dict()})


@users_bp.route("/password", methods=["PUT"])
@jwt_required()
def change_password():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404

    data = request.get_json() or {}
    current_password = data.get("currentPassword", "")
    new_password = data.get("newPassword", "")

    if not user.check_password(current_password):
        return jsonify({"error": "Неверный текущий пароль"}), 401

    if len(new_password) < 6:
        return jsonify({"error": "Новый пароль должен быть минимум 6 символов"}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Пароль изменен"})


@users_bp.route("/purchases", methods=["GET"])
@jwt_required()
def user_purchases():
    uid = int(get_jwt_identity())

    purchases = (
        Purchase.query.filter_by(user_id=uid, payment_status="completed")
        .order_by(Purchase.created_at.desc())
        .all()
    )

    results = []
    for p in purchases:
        doc = Document.query.get(p.document_id)
        results.append({
            "purchase_id": p.id,
            "purchased_at": p.created_at.isoformat() if p.created_at else None,
            "amount": p.amount,
            "document": doc.to_dict() if doc else None,
        })

    return jsonify({"purchases": results})
