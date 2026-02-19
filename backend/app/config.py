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
