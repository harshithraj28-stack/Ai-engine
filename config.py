"""Configuration settings for ResQ-Verse Crisis Action Engine.
Designed for local development and zero-config Google Cloud Run deployment.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Application Metadata
APP_NAME = "ResQ-Verse: Real-Time Multimodal Crisis Action Engine"
APP_VERSION = "1.0.0"
DEBUG = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")

# Server Configuration (Google Cloud Run binds to PORT environment variable)
PORT = int(os.environ.get("PORT", 8080))
HOST = os.environ.get("HOST", "0.0.0.0")

# Security & CORS
SECRET_KEY = os.environ.get("SECRET_KEY", "resqverse-secret-key-prod-cloudrun-2026")
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max payload

# AI & Multimodal Engine (Google Gemini)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", "")).strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")

# Upload and Storage Paths
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
ALLOWED_AUDIO_EXTENSIONS = {"wav", "mp3", "ogg", "m4a", "webm"}

# Triage & Emergency Severity Thresholds
TRIAGE_LEVELS = {
    "RED": {"label": "Immediate / Critical", "color": "#EF4444", "max_response_mins": 5},
    "YELLOW": {"label": "Delayed / Serious", "color": "#F59E0B", "max_response_mins": 15},
    "GREEN": {"label": "Minor / Walking Wounded", "color": "#10B981", "max_response_mins": 60},
    "BLACK": {"label": "Expectant / Deceased", "color": "#6B7280", "max_response_mins": 120},
}
