import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from database.db import db
from database.models import ActivityLog

def log_activity(user_id, action, details=None, ip_address=None):
    """تسجيل نشاط المستخدم"""
    try:
        activity = ActivityLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")

def allowed_file(filename, allowed_extensions):
    """التحقق من نوع الملف"""
    if not filename:
        return False
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, folder, allowed_extensions):
    """حفظ الملف المرفوع"""
    if file and file.filename:
        filename = secure_filename(file.filename)
        
        # التحقق من امتداد الملف
        if not allowed_file(filename, allowed_extensions):
            raise ValueError(f'نوع الملف غير مسموح به. المسموح: {", ".join(allowed_extensions)}')
        
        # إنشاء اسم فريد للملف
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # إنشاء المسار الكامل
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', folder)
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        
        # حفظ الملف
        file.save(file_path)
        return unique_filename
    return None

def generate_access_number(letter_type):
    """إنشاء رقم وصول فريد"""
    from database.models import Letter
    from datetime import datetime
    
    year = datetime.now().year
    prefix = "IN" if letter_type == 'incoming' else "OUT"
    
    # البحث عن آخر رقم لهذا العام
    try:
        last_letter = Letter.query.filter(
            Letter.access_number.like(f"{prefix}-{year}-%")
        ).order_by(Letter.id.desc()).first()
        
        if last_letter:
            try:
                last_number = int(last_letter.access_number.split('-')[-1])
                new_number = last_number + 1
            except:
                new_number = 1
        else:
            new_number = 1
    except:
        new_number = 1
    
    return f"{prefix}-{year}-{new_number:04d}"

def format_date(date_obj):
    """تنسيق التاريخ حسب اللغة"""
    from flask import session
    
    if date_obj:
        if session.get('language') == 'fr':
            return date_obj.strftime('%d/%m/%Y')
        else:  # العربية
            return date_obj.strftime('%Y/%m/%d')
    return ""

def get_file_icon(filename):
    """الحصول على أيقونة الملف حسب النوع"""
    if not filename:
        return "fa-file"
    
    ext = filename.lower().split('.')[-1]
    
    icons = {
        'pdf': 'fa-file-pdf',
        'doc': 'fa-file-word',
        'docx': 'fa-file-word',
        'xls': 'fa-file-excel',
        'xlsx': 'fa-file-excel',
        'ppt': 'fa-file-powerpoint',
        'pptx': 'fa-file-powerpoint',
        'jpg': 'fa-file-image',
        'jpeg': 'fa-file-image',
        'png': 'fa-file-image',
        'gif': 'fa-file-image',
        'txt': 'fa-file-alt',
    }
    
    return icons.get(ext, 'fa-file')