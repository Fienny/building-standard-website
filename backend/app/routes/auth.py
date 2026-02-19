from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

from app import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip()

    if not email or not password or not name:
        return jsonify({"error": "Все поля обязательны"}), 400

    if len(password) < 6:
        return jsonify({"error": "Пароль должен быть минимум 6 символов"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Пользователь с таким email уже существует"}), 400

    user = User(email=email, name=name)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Регистрация успешна",
        "token": token,
        "user": user.to_dict(),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email и пароль обязательны"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Неверный email или пароль"}), 401

    if not user.is_active:
        return jsonify({"error": "Аккаунт деактивирован"}), 403

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Вход выполнен успешно",
        "token": token,
        "user": user.to_dict(),
    })


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404
    return jsonify({"user": user.to_dict()})
