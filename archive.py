from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database.models import Letter
from database.db import db
from utils import log_activity
import json

archive_bp = Blueprint('archive', __name__)

@archive_bp.route('/')
@login_required
def archive_list():
    """عرض الأرشيف"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # الحصول على المراسلات المؤرشفة
    letters = Letter.query.filter_by(is_archived=True)\
        .order_by(Letter.archive_date.desc())\
        .paginate(page=page, per_page=per_page)
    
    # تحويل المرفقات من JSON لكل مراسلة
    for letter in letters.items:
        if letter.attachments:
            try:
                letter.attachments_list = json.loads(letter.attachments)
            except:
                letter.attachments_list = []
        else:
            letter.attachments_list = []
    
    return render_template('archive/list.html', letters=letters)

@archive_bp.route('/restore/<int:letter_id>')
@login_required
def restore_letter(letter_id):
    """استعادة مراسلة من الأرشيف"""
    letter = Letter.query.get_or_404(letter_id)
    
    if not letter.is_archived:
        flash('هذه المراسلة ليست في الأرشيف', 'warning')
        return redirect(url_for('letters.list_letters'))
    
    try:
        letter.is_archived = False
        letter.archive_date = None
        
        db.session.commit()
        
        log_activity(
            current_user.id, 
            'استعادة مراسلة من الأرشيف',
            f'تم استعادة المراسلة برقم: {letter.access_number}'
        )
        
        flash('تم استعادة المراسلة بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء الاستعادة: {str(e)}', 'danger')
    
    return redirect(url_for('archive.archive_list'))