import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://standards_user:password@localhost:5432/standards_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours in seconds

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads/documents")
    PRICE_PER_PAGE = int(os.getenv("PRICE_PER_PAGE", "1000"))
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # Click payment credentials
    CLICK_MERCHANT_ID = os.getenv("CLICK_MERCHANT_ID")
    CLICK_SERVICE_ID = os.getenv("CLICK_SERVICE_ID")
    CLICK_SECRET_KEY = os.getenv("CLICK_SECRET_KEY")

    # PayMe payment credentials
    PAYME_MERCHANT_ID = os.getenv("PAYME_MERCHANT_ID")
    PAYME_SECRET_KEY = os.getenv("PAYME_SECRET_KEY")

    # Card payment credentials (Uzcard/Humo via aggregator)
    CARD_MERCHANT_ID = os.getenv("CARD_MERCHANT_ID")
    CARD_SECRET_KEY = os.getenv("CARD_SECRET_KEY")
    CARD_API_URL = os.getenv("CARD_API_URL")  # e.g., https://api.apelsin.uz
