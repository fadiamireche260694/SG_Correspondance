# ??? ?????????
import os
from datetime import timedelta

class Config:
    """إعدادات التطبيق"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///correspondence.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # إعدادات رفع الملفات
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # الإعدادات المسموح بها
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    ALLOWED_ATTACHMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'}
    
    # إعدادات الجلسة
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # اللغات المدعومة
    LANGUAGES = ['ar', 'fr']
    DEFAULT_LANGUAGE = 'ar'
    
    # إعدادات البريد (اختياري)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')