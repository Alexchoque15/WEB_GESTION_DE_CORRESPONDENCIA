import os
import secrets
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = "correspondencia_super_segura_2026"

    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=30
    )

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False