from flask import Blueprint, render_template, request, flash  # أضف flash هنا
from flask_login import login_required
from database.models import Letter
from forms import SearchForm
from datetime import datetime
import json

search_bp = Blueprint('search', __name__)

@search_bp.route('/advanced', methods=['GET', 'POST'])
@login_required
def advanced_search():
    """البحث المتقدم"""
    form = SearchForm()
    results = []
    
    if form.validate_on_submit():
        try:
            # بناء الاستعلام
            query = Letter.query
            
            # تطبيق فلتر نوع المراسلة
            if form.letter_type.data != 'all':
                query = query.filter(Letter.letter_type == form.letter_type.data)
            
            # تطبيق فلتر تاريخ البدء
            if form.start_date.data:
                query = query.filter(Letter.letter_date >= form.start_date.data)
            
            # تطبيق فلتر تاريخ النهاية
            if form.end_date.data:
                query = query.filter(Letter.letter_date <= form.end_date.data)
            
            # تطبيق البحث حسب النوع
            keyword = form.keyword.data
            if keyword:
                if form.search_type.data == 'all':
                    query = query.filter(
                        (Letter.reference_number.ilike(f'%{keyword}%')) |
                        (Letter.access_number.ilike(f'%{keyword}%')) |
                        (Letter.sender.ilike(f'%{keyword}%')) |
                        (Letter.subject.ilike(f'%{keyword}%')) |
                        (Letter.content.ilike(f'%{keyword}%'))
                    )
                elif form.search_type.data == 'reference_number':
                    query = query.filter(Letter.reference_number.ilike(f'%{keyword}%'))
                elif form.search_type.data == 'access_number':
                    query = query.filter(Letter.access_number.ilike(f'%{keyword}%'))
                elif form.search_type.data == 'sender':
                    query = query.filter(Letter.sender.ilike(f'%{keyword}%'))
                elif form.search_type.data == 'subject':
                    query = query.filter(Letter.subject.ilike(f'%{keyword}%'))
                elif form.search_type.data == 'content':
                    query = query.filter(Letter.content.ilike(f'%{keyword}%'))
            
            # تنفيذ البحث
            results = query.order_by(Letter.created_at.desc()).all()
            
            # تحويل المرفقات من JSON
            for letter in results:
                if letter.attachments:
                    try:
                        letter.attachments_list = json.loads(letter.attachments)
                    except:
                        letter.attachments_list = []
                else:
                    letter.attachments_list = []
            
            flash(f'تم العثور على {len(results)} نتيجة', 'info')
            
        except Exception as e:
            flash(f'حدث خطأ أثناء البحث: {str(e)}', 'danger')
    
    return render_template('search/advanced.html', 
                          form=form, 
                          results=results,
                          now=datetime.now())