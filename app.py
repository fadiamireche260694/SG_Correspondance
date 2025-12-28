from flask import Flask, render_template, request, redirect, url_for, flash, session, g, jsonify
from flask_login import LoginManager, current_user, login_required
from flask_bootstrap import Bootstrap5
from flask_wtf.csrf import CSRFProtect
from config.config import Config
from database.db import db
import os
from datetime import datetime, timedelta

def create_app():
    """إنشاء وتكوين تطبيق Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # إضافة CSRF حماية
    csrf = CSRFProtect(app)
    
    # إعداد ترميز UTF-8 للاستجابات
    @app.after_request
    def add_charset(response):
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
    
    # تهيئة الإضافات
    db.init_app(app)
    Bootstrap5(app)
    
    # إعداد Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'الرجاء تسجيل الدخول للوصول إلى هذه الصفحة'
    login_manager.login_message_category = 'warning'
    
    from database.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # استيراد البلوبنتات بعد إنشاء التطبيق
    from auth import auth_bp
    from letters import letters_bp
    from archive import archive_bp
    from search import search_bp
    
    # معالج قبل كل طلب
    @app.before_request
    def before_request():
        g.current_user = current_user
        # تعيين اللغة من الجلسة أو استخدام الافتراضي
        if 'language' not in session:
            session['language'] = app.config['DEFAULT_LANGUAGE']
    
    # تسجيل البلوبنتات
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(letters_bp, url_prefix='/letters')
    app.register_blueprint(archive_bp, url_prefix='/archive')
    app.register_blueprint(search_bp, url_prefix='/search')
    
    # الصفحة الرئيسية
    @app.route('/')
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return render_template('index.html')
    
    # تغيير اللغة
    @app.route('/lang/<lang>')
    def change_language(lang):
        if lang in app.config['LANGUAGES']:
            session['language'] = lang
        return redirect(request.referrer or url_for('index'))
    
    # API للإحصائيات
    @app.route('/api/stats')
    @login_required
    def get_stats_api():
        """API للحصول على الإحصائيات"""
        from database.models import Letter, User
        
        try:
            incoming_count = Letter.query.filter_by(
                letter_type='incoming',
                is_archived=False
            ).count()
            
            outgoing_count = Letter.query.filter_by(
                letter_type='outgoing',
                is_archived=False
            ).count()
            
            archived_count = Letter.query.filter_by(
                is_archived=True
            ).count()
            
            users_count = User.query.count()
            total_letters = Letter.query.count()
            
            # الحصول على الإحصائيات الشهرية
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            monthly_incoming = Letter.query.filter(
                Letter.letter_type == 'incoming',
                db.extract('year', Letter.created_at) == current_year,
                db.extract('month', Letter.created_at) == current_month
            ).count()
            
            monthly_outgoing = Letter.query.filter(
                Letter.letter_type == 'outgoing',
                db.extract('year', Letter.created_at) == current_year,
                db.extract('month', Letter.created_at) == current_month
            ).count()
            
            return jsonify({
                'success': True,
                'incoming_count': incoming_count,
                'outgoing_count': outgoing_count,
                'archived_count': archived_count,
                'users_count': users_count,
                'total_letters': total_letters,
                'monthly_incoming': monthly_incoming,
                'monthly_outgoing': monthly_outgoing
            })
        except Exception as e:
            app.logger.error(f"Error in stats API: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # معالج context لجميع القوالب
    @app.context_processor
    def inject_functions():
        """حقن الدوال والإحصائيات في جميع القوالب"""
        from database.models import Letter, User, ActivityLog
        
        def get_stats():
            """الحصول على الإحصائيات"""
            stats = {
                'incoming_count': 0,
                'outgoing_count': 0,
                'archived_count': 0,
                'users_count': 0,
                'total_letters': 0,
                'monthly_incoming': 0,
                'monthly_outgoing': 0
            }
            
            try:
                if current_user.is_authenticated:
                    # إحصائيات المراسلات
                    stats['incoming_count'] = Letter.query.filter_by(
                        letter_type='incoming',
                        is_archived=False
                    ).count()
                    
                    stats['outgoing_count'] = Letter.query.filter_by(
                        letter_type='outgoing',
                        is_archived=False
                    ).count()
                    
                    stats['archived_count'] = Letter.query.filter_by(
                        is_archived=True
                    ).count()
                    
                    stats['users_count'] = User.query.count()
                    stats['total_letters'] = Letter.query.count()
                    
                    # إحصائيات الشهر الحالي
                    current_month = datetime.now().month
                    current_year = datetime.now().year
                    
                    stats['monthly_incoming'] = Letter.query.filter(
                        Letter.letter_type == 'incoming',
                        db.extract('year', Letter.created_at) == current_year,
                        db.extract('month', Letter.created_at) == current_month
                    ).count()
                    
                    stats['monthly_outgoing'] = Letter.query.filter(
                        Letter.letter_type == 'outgoing',
                        db.extract('year', Letter.created_at) == current_year,
                        db.extract('month', Letter.created_at) == current_month
                    ).count()
                    
            except Exception as e:
                app.logger.error(f"Error getting stats: {str(e)}")
            
            return stats
        
        def get_latest_letters(limit=5):
            """الحصول على أحدث المراسلات"""
            try:
                if current_user.is_authenticated:
                    return Letter.query.filter_by(is_archived=False)\
                        .order_by(Letter.created_at.desc())\
                        .limit(limit).all()
            except Exception as e:
                app.logger.error(f"Error getting latest letters: {str(e)}")
            return []
        
        def get_recent_activity(days=7):
            """النشاطات الأخيرة"""
            try:
                if current_user.is_authenticated:
                    since_date = datetime.utcnow() - timedelta(days=days)
                    return ActivityLog.query.filter(
                        ActivityLog.created_at >= since_date
                    ).count()
            except Exception as e:
                app.logger.error(f"Error getting recent activity: {str(e)}")
            return 0
        
        def get_yearly_stats(year=None):
            """إحصائيات سنوية"""
            try:
                if current_user.is_authenticated:
                    if year is None:
                        year = datetime.now().year
                    
                    incoming_yearly = Letter.query.filter(
                        Letter.letter_type == 'incoming',
                        db.extract('year', Letter.created_at) == year
                    ).count()
                    
                    outgoing_yearly = Letter.query.filter(
                        Letter.letter_type == 'outgoing',
                        db.extract('year', Letter.created_at) == year
                    ).count()
                    
                    return {
                        'year': year,
                        'incoming': incoming_yearly,
                        'outgoing': outgoing_yearly,
                        'total': incoming_yearly + outgoing_yearly
                    }
            except Exception as e:
                app.logger.error(f"Error getting yearly stats: {str(e)}")
            return {'year': year or datetime.now().year, 'incoming': 0, 'outgoing': 0, 'total': 0}
        
        def get_top_senders(limit=5):
            """أكثر الباعثين تكراراً"""
            try:
                if current_user.is_authenticated:
                    from sqlalchemy import func
                    
                    result = db.session.query(
                        Letter.sender,
                        func.count(Letter.id).label('count')
                    ).group_by(Letter.sender)\
                     .order_by(func.count(Letter.id).desc())\
                     .limit(limit).all()
                    
                    return [{'sender': r[0], 'count': r[1]} for r in result]
            except Exception as e:
                app.logger.error(f"Error getting top senders: {str(e)}")
            return []
        
        def get_current_year():
            """السنة الحالية"""
            return datetime.now().year
        
        def format_number(num):
            """تنسيق الأرقام"""
            try:
                return f"{int(num):,}".replace(',', '،')
            except:
                return str(num)
        
        def get_blueprint_names():
            """أسماء البلوبنتات المسجلة"""
            return [bp.name for bp in app.blueprints.values()]
        
        return dict(
            get_stats=get_stats,
            get_latest_letters=get_latest_letters,
            get_recent_activity=get_recent_activity,
            get_yearly_stats=get_yearly_stats,
            get_top_senders=get_top_senders,
            get_current_year=get_current_year,
            format_number=format_number,
            blueprints=get_blueprint_names(),
            now=datetime.now,
            config=app.config
        )
    
    # معالج الأخطاء
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"500 error: {str(e)}")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(401)
    def unauthorized(e):
        return redirect(url_for('auth.login'))
    
    # API للمخططات
    @app.route('/api/chart-data')
    @login_required
    def get_chart_data():
        """API لبيانات المخططات"""
        try:
            from database.models import Letter
            
            # بيانات الأشهر الـ 6 الماضية
            months = []
            incoming_data = []
            outgoing_data = []
            
            current_date = datetime.now()
            for i in range(5, -1, -1):
                month_date = current_date.replace(day=1)
                for _ in range(i):
                    # الذهاب للشهر السابق
                    month_date = month_date.replace(day=1) - timedelta(days=1)
                    month_date = month_date.replace(day=1)
                
                month_name = month_date.strftime('%Y-%m')
                months.append(month_date.strftime('%b %Y'))
                
                year = month_date.year
                month = month_date.month
                
                incoming = Letter.query.filter(
                    Letter.letter_type == 'incoming',
                    db.extract('year', Letter.created_at) == year,
                    db.extract('month', Letter.created_at) == month
                ).count()
                
                outgoing = Letter.query.filter(
                    Letter.letter_type == 'outgoing',
                    db.extract('year', Letter.created_at) == year,
                    db.extract('month', Letter.created_at) == month
                ).count()
                
                incoming_data.append(incoming)
                outgoing_data.append(outgoing)
            
            return jsonify({
                'success': True,
                'labels': months,
                'datasets': [
                    {
                        'label': 'المراسلات الواردة',
                        'data': incoming_data,
                        'backgroundColor': 'rgba(13, 110, 253, 0.8)',
                        'borderColor': 'rgba(13, 110, 253, 1)'
                    },
                    {
                        'label': 'المراسلات الصادرة',
                        'data': outgoing_data,
                        'backgroundColor': 'rgba(25, 135, 84, 0.8)',
                        'borderColor': 'rgba(25, 135, 84, 1)'
                    }
                ]
            })
            
        except Exception as e:
            app.logger.error(f"Error in chart data API: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # API للنشاطات الأخيرة
    @app.route('/api/recent-activity')
    @login_required
    def get_recent_activity_api():
        """API للنشاطات الأخيرة"""
        try:
            from database.models import ActivityLog, User
            
            activities = ActivityLog.query\
                .join(User, ActivityLog.user_id == User.id)\
                .add_columns(User.username, User.full_name)\
                .order_by(ActivityLog.created_at.desc())\
                .limit(10)\
                .all()
            
            activity_list = []
            for activity, username, full_name in activities:
                activity_list.append({
                    'id': activity.id,
                    'action': activity.action,
                    'details': activity.details,
                    'username': username,
                    'full_name': full_name,
                    'created_at': activity.created_at.strftime('%Y-%m-%d %H:%M'),
                    'time_ago': get_time_ago(activity.created_at)
                })
            
            return jsonify({
                'success': True,
                'activities': activity_list
            })
            
        except Exception as e:
            app.logger.error(f"Error in activity API: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def get_time_ago(dt):
        """الحصول على الوقت المنقضي"""
        now = datetime.utcnow()
        diff = now - dt
        
        if diff.days > 365:
            years = diff.days // 365
            return f"قبل {years} سنة"
        elif diff.days > 30:
            months = diff.days // 30
            return f"قبل {months} شهر"
        elif diff.days > 0:
            return f"قبل {diff.days} يوم"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"قبل {hours} ساعة"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"قبل {minutes} دقيقة"
        else:
            return "الآن"
    
    # إضافة دالة للمساعدة في القوالب
    @app.template_filter('datetime_format')
    def datetime_format(value, format='%Y-%m-%d %H:%M'):
        """فلتر لتنسيق التواريخ"""
        if value is None:
            return ""
        return value.strftime(format)
    
    @app.template_filter('date_format')
    def date_format(value, format='%Y-%m-%d'):
        """فلتر لتنسيق التواريخ فقط"""
        if value is None:
            return ""
        return value.strftime(format)
    
    @app.template_filter('time_ago')
    def time_ago_filter(value):
        """فلتر للوقت المنقضي"""
        if value is None:
            return ""
        return get_time_ago(value)
    
    # إنشاء مجلدات الرفع إذا لم تكن موجودة
    with app.app_context():
        # مجلدات الرفع
        upload_folders = [
            app.config['UPLOAD_FOLDER'],
            os.path.join(app.config['UPLOAD_FOLDER'], 'letters'),
            os.path.join(app.config['UPLOAD_FOLDER'], 'attachments'),
        ]
        
        # مجلدات النظام
        system_folders = [
            'static/uploads',
            'static/uploads/letters',
            'static/uploads/attachments',
            'templates/errors',
            'database'
        ]
        
        for folder in upload_folders + system_folders:
            full_path = os.path.join(app.root_path, folder)
            if not os.path.exists(full_path):
                os.makedirs(full_path, exist_ok=True)
                app.logger.info(f"Created folder: {full_path}")
        
        # إنشاء جدول المستخدمين إذا لم يكن موجوداً
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # إعدادات التطوير
    if app.config.get('DEBUG', True):
        app.logger.setLevel('DEBUG')
        app.logger.info("Running in DEBUG mode")
    else:
        app.logger.setLevel('INFO')
    
    # تشغيل التطبيق
    app.run(
        debug=app.config.get('DEBUG', True),
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000)
    )