from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

INSTANCE_DIR = BASE_DIR / 'instance'
INSTANCE_DIR.mkdir(exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{INSTANCE_DIR / 'cinema.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024

    TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '')
    TMDB_IMAGE_BASE = os.environ.get('TMDB_IMAGE_BASE', 'https://image.tmdb.org/t/p/w500')
