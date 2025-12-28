from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from datetime import datetime
from database.db import db
from database.models import Letter
from forms_letters import LetterForm
from utils import log_activity, save_uploaded_file, generate_access_number
import json
import os

letters_bp = Blueprint('letters', __name__)

@letters_bp.route('/add/incoming', methods=['GET', 'POST'])
@login_required
def add_incoming():
    """إضافة مراسلة واردة"""
    form = LetterForm()
    form.letter_type.data = 'incoming'  # تعيين القيمة الافتراضية
    
    # إزالة التحقق من رقم الوصول من النموذج
    form.access_number.validators = []  # إزالة جميع validators
    
    if request.method == 'POST':
        # التحقق من صحة النموذج يدوياً
        errors = []
        
        # التحقق من الحقول المطلوبة
        required_fields = ['reference_number', 'sender', 'subject', 'letter_date', 'access_date']
        for field in required_fields:
            if not request.form.get(field):
                errors.append(f'حقل {field} مطلوب')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            try:
                # إنشاء رقم وصول تلقائياً
                access_number = generate_access_number('incoming')
                
                # حفظ الملفات
                letter_image = None
                attachments_list = []
                
                # تحميل صورة المراسلة
                if 'letter_image' in request.files:
                    file = request.files['letter_image']
                    if file and file.filename:
                        try:
                            letter_image = save_uploaded_file(
                                file, 
                                'letters', 
                                current_app.config['ALLOWED_IMAGE_EXTENSIONS']
                            )
                        except ValueError as e:
                            flash(f'خطأ في صورة المراسلة: {str(e)}', 'danger')
                            return redirect(url_for('letters.add_incoming'))
                
                # تحميل المرفقات
                if 'attachments' in request.files:
                    file = request.files['attachments']
                    if file and file.filename:
                        try:
                            attachment = save_uploaded_file(
                                file, 
                                'attachments',
                                current_app.config['ALLOWED_ATTACHMENT_EXTENSIONS']
                            )
                            if attachment:
                                attachments_list.append(attachment)
                        except ValueError as e:
                            flash(f'خطأ في المرفق: {str(e)}', 'danger')
                            return redirect(url_for('letters.add_incoming'))
                
                # إنشاء المراسلة
                letter = Letter(
                    letter_type='incoming',
                    reference_number=request.form.get('reference_number'),
                    access_number=access_number,
                    sender=request.form.get('sender'),
                    receiver=request.form.get('receiver'),
                    subject=request.form.get('subject'),
                    content=request.form.get('content'),
                    letter_date=datetime.strptime(request.form.get('letter_date'), '%Y-%m-%d'),
                    access_date=datetime.strptime(request.form.get('access_date'), '%Y-%m-%d'),
                    response_date=datetime.strptime(request.form.get('response_date'), '%Y-%m-%d') if request.form.get('response_date') else None,
                    response_number=request.form.get('response_number'),
                    letter_image=letter_image,
                    attachments=json.dumps(attachments_list) if attachments_list else None,
                    user_id=current_user.id
                )
                
                db.session.add(letter)
                db.session.commit()
                
                # تسجيل النشاط
                log_activity(
                    current_user.id, 
                    'إضافة مراسلة واردة',
                    f'تم إضافة مراسلة واردة برقم: {access_number}'
                )
                
                flash(f'تم إضافة المراسلة الواردة بنجاح! رقم الوصول: {access_number}', 'success')
                return redirect(url_for('letters.view_letter', letter_id=letter.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'حدث خطأ أثناء الإضافة: {str(e)}', 'danger')
    
    return render_template('letters/add_incoming.html', form=form)

@letters_bp.route('/add/outgoing', methods=['GET', 'POST'])
@login_required
def add_outgoing():
    """إضافة مراسلة صادرة"""
    form = LetterForm()
    form.letter_type.data = 'outgoing'  # تعيين القيمة الافتراضية
    
    # إزالة التحقق من رقم الوصول من النموذج
    form.access_number.validators = []  # إزالة جميع validators
    
    if request.method == 'POST':
        # التحقق من صحة النموذج يدوياً
        errors = []
        
        # التحقق من الحقول المطلوبة
        required_fields = ['reference_number', 'sender', 'receiver', 'subject', 'letter_date', 'access_date']
        for field in required_fields:
            if not request.form.get(field):
                errors.append(f'حقل {field} مطلوب')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            try:
                # إنشاء رقم وصول تلقائياً
                access_number = generate_access_number('outgoing')
                
                # حفظ الملفات
                letter_image = None
                attachments_list = []
                
                # تحميل صورة المراسلة
                if 'letter_image' in request.files:
                    file = request.files['letter_image']
                    if file and file.filename:
                        try:
                            letter_image = save_uploaded_file(
                                file, 
                                'letters', 
                                current_app.config['ALLOWED_IMAGE_EXTENSIONS']
                            )
                        except ValueError as e:
                            flash(f'خطأ في صورة المراسلة: {str(e)}', 'danger')
                            return redirect(url_for('letters.add_outgoing'))
                
                # تحميل المرفقات
                if 'attachments' in request.files:
                    file = request.files['attachments']
                    if file and file.filename:
                        try:
                            attachment = save_uploaded_file(
                                file, 
                                'attachments',
                                current_app.config['ALLOWED_ATTACHMENT_EXTENSIONS']
                            )
                            if attachment:
                                attachments_list.append(attachment)
                        except ValueError as e:
                            flash(f'خطأ في المرفق: {str(e)}', 'danger')
                            return redirect(url_for('letters.add_outgoing'))
                
                # إنشاء المراسلة
                letter = Letter(
                    letter_type='outgoing',
                    reference_number=request.form.get('reference_number'),
                    access_number=access_number,
                    sender=request.form.get('sender'),
                    receiver=request.form.get('receiver'),
                    subject=request.form.get('subject'),
                    content=request.form.get('content'),
                    letter_date=datetime.strptime(request.form.get('letter_date'), '%Y-%m-%d'),
                    access_date=datetime.strptime(request.form.get('access_date'), '%Y-%m-%d'),
                    response_date=datetime.strptime(request.form.get('response_date'), '%Y-%m-%d') if request.form.get('response_date') else None,
                    response_number=request.form.get('response_number'),
                    letter_image=letter_image,
                    attachments=json.dumps(attachments_list) if attachments_list else None,
                    user_id=current_user.id
                )
                
                db.session.add(letter)
                db.session.commit()
                
                # تسجيل النشاط
                log_activity(
                    current_user.id, 
                    'إضافة مراسلة صادرة',
                    f'تم إضافة مراسلة صادرة برقم: {access_number}'
                )
                
                flash(f'تم إضافة المراسلة الصادرة بنجاح! رقم الوصول: {access_number}', 'success')
                return redirect(url_for('letters.view_letter', letter_id=letter.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'حدث خطأ أثناء الإضافة: {str(e)}', 'danger')
    
    return render_template('letters/add_outgoing.html', form=form)

@letters_bp.route('/list')
@login_required
def list_letters():
    """عرض قائمة المراسلات"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # الحصول على المراسلات
    letters = Letter.query.filter_by(is_archived=False)\
        .order_by(Letter.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return render_template('letters/list.html', letters=letters)

@letters_bp.route('/view/<int:letter_id>')
@login_required
def view_letter(letter_id):
    """عرض تفاصيل المراسلة"""
    letter = Letter.query.get_or_404(letter_id)
    
    # تحويل المرفقات من JSON
    attachments = []
    if letter.attachments:
        try:
            attachments = json.loads(letter.attachments)
        except:
            attachments = []
    
    return render_template('letters/view.html', letter=letter, attachments=attachments)

@letters_bp.route('/edit/<int:letter_id>', methods=['GET', 'POST'])
@login_required
def edit_letter(letter_id):
    """تعديل المراسلة"""
    letter = Letter.query.get_or_404(letter_id)
    
    # التحقق من صلاحية المستخدم
    if letter.user_id != current_user.id and not current_user.is_admin():
        flash('ليس لديك صلاحية لتعديل هذه المراسلة', 'danger')
        return redirect(url_for('letters.view_letter', letter_id=letter_id))
    
    form = LetterForm(obj=letter)
    
    if form.validate_on_submit():
        try:
            letter.reference_number = form.reference_number.data
            letter.sender = form.sender.data
            letter.receiver = form.receiver.data
            letter.subject = form.subject.data
            letter.content = form.content.data
            letter.letter_date = form.letter_date.data
            letter.access_date = form.access_date.data
            letter.response_date = form.response_date.data
            letter.response_number = form.response_number.data
            
            # تحديث المرفقات إذا تم رفع ملفات جديدة
            if 'letter_image' in request.files:
                file = request.files['letter_image']
                if file and file.filename:
                    letter.letter_image = save_uploaded_file(
                        file, 
                        'letters', 
                        current_app.config['ALLOWED_IMAGE_EXTENSIONS']
                    )
            
            db.session.commit()
            
            log_activity(
                current_user.id, 
                'تعديل مراسلة',
                f'تم تعديل المراسلة برقم: {letter.access_number}'
            )
            
            flash('تم تعديل المراسلة بنجاح!', 'success')
            return redirect(url_for('letters.view_letter', letter_id=letter.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء التعديل: {str(e)}', 'danger')
    
    return render_template('letters/edit.html', form=form, letter=letter)

@letters_bp.route('/delete/<int:letter_id>')
@login_required
def delete_letter(letter_id):
    """حذف المراسلة"""
    letter = Letter.query.get_or_404(letter_id)
    
    # التحقق من صلاحية المستخدم
    if not current_user.is_admin():
        flash('ليس لديك صلاحية لحذف المراسلات', 'danger')
        return redirect(url_for('letters.list_letters'))
    
    try:
        log_activity(
            current_user.id, 
            'حذف مراسلة',
            f'تم حذف المراسلة برقم: {letter.access_number}'
        )
        
        db.session.delete(letter)
        db.session.commit()
        
        flash('تم حذف المراسلة بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء الحذف: {str(e)}', 'danger')
    
    return redirect(url_for('letters.list_letters'))

@letters_bp.route('/archive/<int:letter_id>')
@login_required
def archive_letter(letter_id):
    """أرشفة المراسلة"""
    letter = Letter.query.get_or_404(letter_id)
    
    try:
        letter.is_archived = True
        letter.archive_date = datetime.utcnow()
        
        db.session.commit()
        
        log_activity(
            current_user.id, 
            'أرشفة مراسلة',
            f'تم أرشفة المراسلة برقم: {letter.access_number}'
        )
        
        flash('تم أرشفة المراسلة بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء الأرشفة: {str(e)}', 'danger')
    
    return redirect(url_for('letters.list_letters'))

@letters_bp.route('/download/letter_image/<filename>')
@login_required
def download_letter_image(filename):
    """تحميل صورة المراسلة"""
    try:
        # التحقق من أن الملف موجود
        uploads_path = os.path.join(current_app.root_path, 'static', 'uploads', 'letters')
        
        # التحقق من أن المسار آمن
        if not os.path.exists(uploads_path):
            flash('مجلد التحميل غير موجود', 'danger')
            return redirect(url_for('letters.list_letters'))
        
        return send_from_directory(uploads_path, filename, as_attachment=True)
        
    except FileNotFoundError:
        flash('الملف غير موجود', 'danger')
        return redirect(url_for('letters.list_letters'))
    except Exception as e:
        flash(f'حدث خطأ أثناء التحميل: {str(e)}', 'danger')
        return redirect(url_for('letters.list_letters'))

@letters_bp.route('/download/attachment/<filename>')
@login_required
def download_attachment(filename):
    """تحميل مرفق"""
    try:
        # التحقق من أن الملف موجود
        uploads_path = os.path.join(current_app.root_path, 'static', 'uploads', 'attachments')
        
        # التحقق من أن المسار آمن
        if not os.path.exists(uploads_path):
            flash('مجلد المرفقات غير موجود', 'danger')
            return redirect(url_for('letters.list_letters'))
        
        return send_from_directory(uploads_path, filename, as_attachment=True)
        
    except FileNotFoundError:
        flash('الملف غير موجود', 'danger')
        return redirect(url_for('letters.list_letters'))
    except Exception as e:
        flash(f'حدث خطأ أثناء التحميل: {str(e)}', 'danger')
        return redirect(url_for('letters.list_letters'))