import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'landvault-ai-secret-key-2026')
    DATABASE = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'landvault.db'))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'uploads'))
    SAMPLE_DOCS_FOLDER = os.path.join(BASE_DIR, 'sample_docs')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB limit
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    
    # OCR and Confidence Thresholds
    CONFIDENCE_HIGH_THRESHOLD = 85.0
    CONFIDENCE_MEDIUM_THRESHOLD = 70.0
    DUPLICATE_SIMILARITY_THRESHOLD = 0.80
    SEND_FILE_MAX_AGE_DEFAULT = 0
