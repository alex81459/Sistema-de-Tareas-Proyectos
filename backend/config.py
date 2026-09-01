import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_REFRESH_COOKIE_NAME = "refresh_token"
    JWT_REFRESH_COOKIE_PATH = "/api/v1/autenticacion"
    JWT_COOKIE_SECURE = APP_ENV == "production"
    JWT_COOKIE_SAMESITE = "Strict"
    JWT_COOKIE_CSRF_PROTECT = True

    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    TRUST_PROXY = os.getenv("TRUST_PROXY", "false").strip().lower() == "true"

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:4200").split(",")

    @classmethod
    def validate(cls):
        required_settings = {
            "DATABASE_URL": cls.SQLALCHEMY_DATABASE_URI,
            "SECRET_KEY": cls.SECRET_KEY,
            "JWT_SECRET_KEY": cls.JWT_SECRET_KEY,
        }
        missing = [name for name, value in required_settings.items() if not value]
        if missing:
            missing_values = ", ".join(sorted(missing))
            raise RuntimeError(
                "Faltan variables de entorno requeridas: "
                f"{missing_values}. Copia .env.example a .env y completa sus valores."
            )

        if cls.APP_ENV == "production" and not cls.CORS_ORIGINS:
            raise RuntimeError("CORS_ORIGINS es obligatoria cuando APP_ENV=production.")
