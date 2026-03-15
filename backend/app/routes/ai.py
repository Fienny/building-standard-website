"""
AI Assistant proxy routes
Проксирует запросы к Django AI backend
"""

from flask import Blueprint, request, jsonify
import requests
import os

ai_bp = Blueprint("ai", __name__)

# URL Django AI backend (настраивается через env)
AI_BACKEND_URL = os.getenv("AI_BACKEND_URL", "http://localhost:8000")


@ai_bp.route("/chat", methods=["POST"])
def chat():
    """
    Прокси для AI чата
    Перенаправляет запросы к Django backend
    """
    data = request.get_json() or {}
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "Сообщение не может быть пустым"}), 400

    try:
        # Отправляем запрос к Django AI backend
        response = requests.post(
            f"{AI_BACKEND_URL}/api/chat/",
            json={"message": message},
            timeout=60,  # AI может работать долго
        )

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            return jsonify({
                "error": error_data.get("error", "Ошибка AI backend"),
                "details": error_data
            }), response.status_code

    except requests.Timeout:
        return jsonify({"error": "Превышено время ожидания ответа от AI"}), 504

    except requests.ConnectionError:
        return jsonify({
            "error": "AI-помощник временно недоступен",
            "hint": "Проверьте, запущен ли Django AI backend"
        }), 503

    except Exception as e:
        return jsonify({"error": f"Внутренняя ошибка: {str(e)}"}), 500
