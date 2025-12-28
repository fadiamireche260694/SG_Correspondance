from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from datetime import date
import re

class LoginForm(FlaskForm):
    """نموذج تسجيل الدخول"""
    username = StringField('اسم المستخدم', validators=[DataRequired(message="اسم المستخدم مطلوب")])
    password = PasswordField('كلمة المرور', validators=[DataRequired(message="كلمة المرور مطلوبة")])
    remember = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

class RegistrationForm(FlaskForm):
    """نموذج إنشاء حساب"""
    username = StringField('اسم المستخدم', validators=[
        DataRequired(message="اسم المستخدم مطلوب"),
        Length(min=3, max=80, message="اسم المستخدم يجب أن يكون بين 3 و 80 حرف"),
        lambda form, field: ValidationError('اسم المستخدم غير مسموح') if re.search(r'[^\w.@+-]', field.data) else None
    ])
    email = StringField('البريد الإلكتروني', validators=[
        DataRequired(message="البريد الإلكتروني مطلوب"),
        Email(message="البريد الإلكتروني غير صحيح")
    ])
    full_name = StringField('الاسم الكامل', validators=[
        DataRequired(message="الاسم الكامل مطلوب"),
        Length(min=3, max=100, message="الاسم يجب أن يكون بين 3 و 100 حرف")
    ])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message="كلمة المرور مطلوبة"),
        Length(min=6, message="كلمة المرور يجب أن تكون 6 أحرف على الأقل")
    ])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[
        DataRequired(message="تأكيد كلمة المرور مطلوب"),
        EqualTo('password', message='كلمات المرور غير متطابقة')
    ])
    submit = SubmitField('إنشاء حساب')

class SearchForm(FlaskForm):
    """نموذج البحث"""
    search_type = SelectField('نوع البحث', choices=[
        ('all', 'الكل'),
        ('reference_number', 'رقم الرسالة'),
        ('access_number', 'رقم الوصول'),
        ('sender', 'الباعث'),
        ('subject', 'الموضوع'),
        ('content', 'المحتوى')
    ], default='all')
    
    keyword = StringField('كلمة البحث', validators=[DataRequired(message="كلمة البحث مطلوبة")])
    
    letter_type = SelectField('نوع المراسلة', choices=[
        ('all', 'الكل'),
        ('incoming', 'وارد فقط'),
        ('outgoing', 'صادر فقط')
    ], default='all')
    
    start_date = DateField('من تاريخ', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('إلى تاريخ', format='%Y-%m-%d', validators=[Optional()])
    
    submit = SubmitField('بحث')