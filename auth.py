from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import db
from database.models import User, ActivityLog
from forms import LoginForm, RegistrationForm
from utils import log_activity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('الحساب معطل، الرجاء الاتصال بالمسؤول', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=form.remember.data)
            
            # تسجيل النشاط
            log_activity(user.id, 'تسجيل الدخول', f'تسجيل دخول المستخدم {user.username}')
            
            flash('تم تسجيل الدخول بنجاح!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """صفحة إنشاء حساب جديد"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # التحقق من وجود المستخدم
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            if existing_user.username == form.username.data:
                flash('اسم المستخدم موجود بالفعل', 'danger')
            else:
                flash('البريد الإلكتروني موجود بالفعل', 'danger')
            return redirect(url_for('auth.register'))
        
        # إنشاء مستخدم جديد
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            role='user'
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # تسجيل النشاط
        log_activity(user.id, 'إنشاء حساب', f'إنشاء حساب جديد للمستخدم {user.username}')
        
        flash('تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول', 'success')
        return redirect(url_for('auth.login'))
    else:
        # عرض أخطاء التحقق إذا وجدت
        if request.method == 'POST':
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'خطأ في {getattr(form, field).label.text}: {error}', 'danger')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    # تسجيل النشاط
    log_activity(current_user.id, 'تسجيل الخروج', f'تسجيل خروج المستخدم {current_user.username}')
    
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('auth.login'))