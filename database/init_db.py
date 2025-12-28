# ????? ????? ????????
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.db import db
from database.models import User

def init_database():
    """تهيئة قاعدة البيانات"""
    app = create_app()
    
    with app.app_context():
        # إنشاء الجداول
        db.create_all()
        
        # إنشاء مستخدم مسؤول افتراضي
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='مدير النظام'
            )
            admin.set_password('admin123')
            admin.role = 'admin'
            db.session.add(admin)
            db.session.commit()
            print("✅ تم إنشاء مستخدم المسؤول بنجاح")
        
        print("✅ تم تهيئة قاعدة البيانات بنجاح")

if __name__ == '__main__':
    init_database()