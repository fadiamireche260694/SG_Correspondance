# ????? ????????
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .db import db

class User(UserMixin, db.Model):
    """نموذج المستخدم"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    letters = db.relationship('Letter', backref='creator', lazy=True)
    
    def set_password(self, password):
        """تشفير كلمة المرور"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """التحقق إذا كان المستخدم مدير"""
        return self.role == 'admin'
    
    def is_archivist(self):
        """التحقق إذا كان المستخدم أمين أرشيف"""
        return self.role == 'archivist'

class Letter(db.Model):
    """نموذج المراسلات"""
    __tablename__ = 'letters'
    
    id = db.Column(db.Integer, primary_key=True)
    letter_type = db.Column(db.String(20), nullable=False)  # incoming/outgoing
    reference_number = db.Column(db.String(50), unique=True, nullable=False)
    access_number = db.Column(db.String(50), unique=True, nullable=False)
    sender = db.Column(db.String(200), nullable=False)
    receiver = db.Column(db.String(200))
    subject = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text)
    
    # التواريخ
    letter_date = db.Column(db.Date, nullable=False)
    access_date = db.Column(db.Date, nullable=False)
    response_date = db.Column(db.Date)
    response_number = db.Column(db.String(50))
    
    # الملفات
    letter_image = db.Column(db.String(500))
    attachments = db.Column(db.Text)  # JSON list of attachments
    
    # حالة المراسلة
    status = db.Column(db.String(20), default='new')
    is_archived = db.Column(db.Boolean, default=False)
    archive_date = db.Column(db.DateTime)
    
    # العلاقات
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # التواريخ التلقائية
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Archive(db.Model):
    """نموذج الأرشيف"""
    __tablename__ = 'archives'
    
    id = db.Column(db.Integer, primary_key=True)
    letter_id = db.Column(db.Integer, db.ForeignKey('letters.id'), nullable=False)
    archive_reason = db.Column(db.String(200))
    archived_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    archived_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    letter = db.relationship('Letter', backref='archive_record', lazy=True)
    archiver = db.relationship('User', backref='archived_letters', lazy=True)

class ActivityLog(db.Model):
    """سجل النشاطات"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = db.relationship('User', backref='activities', lazy=True)