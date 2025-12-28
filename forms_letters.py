from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from datetime import date
import re

class LetterForm(FlaskForm):
    """نموذج إضافة مراسلة"""
    letter_type = SelectField('نوع المراسلة', choices=[
        ('incoming', 'وارد'),
        ('outgoing', 'صادر')
    ], validators=[DataRequired(message="نوع المراسلة مطلوب")])
    
    reference_number = StringField('رقم الرسالة', validators=[DataRequired(message="رقم الرسالة مطلوب")])
    access_number = StringField('رقم الوصول', validators=[Optional()])  # اختياري
    
    sender = StringField('الباعث', validators=[DataRequired(message="اسم الباعث مطلوب")])
    receiver = StringField('المستلم', validators=[Optional()])
    
    subject = StringField('الموضوع', validators=[DataRequired(message="موضوع المراسلة مطلوب")])
    content = TextAreaField('المحتوى', validators=[Optional()])
    
    letter_date = DateField('تاريخ الرسالة', format='%Y-%m-%d', validators=[DataRequired(message="تاريخ الرسالة مطلوب")])
    access_date = DateField('تاريخ الوصول', format='%Y-%m-%d', validators=[DataRequired(message="تاريخ الوصول مطلوب")])
    response_date = DateField('تاريخ الرد', format='%Y-%m-%d', validators=[Optional()])
    response_number = StringField('رقم الرد', validators=[Optional()])
    
    letter_image = FileField('صورة المراسلة', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'pdf'], 'الصور و PDF فقط!')
    ])
    
    attachments = FileField('المرفقات', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'], 'الملفات المسموح بها فقط!')
    ])
    
    submit = SubmitField('حفظ المراسلة')
    
    def validate_letter_date(self, field):
        if field.data and field.data > date.today():
            raise ValidationError('لا يمكن أن يكون تاريخ الرسالة في المستقبل')
    
    def validate_access_date(self, field):
        if field.data and field.data > date.today():
            raise ValidationError('لا يمكن أن يكون تاريخ الوصول في المستقبل')