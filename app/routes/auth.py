# ============================================================
# app/routes/auth.py - Blueprint xác thực người dùng
# Chứa: Đăng ký, Đăng nhập, Đăng xuất
# URL prefix: /auth/
# ============================================================

import bcrypt
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .. import db
from ..models import User
from ..forms import RegisterForm, LoginForm
from ..utils import generate_uuid

# Tạo Blueprint với tên 'auth'
auth_bp = Blueprint('auth', __name__)


# ============================================================
# Route: GET/POST /auth/register - Đăng ký tài khoản mới
# ============================================================
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    GET:  Hiển thị form đăng ký.
    POST: Xử lý dữ liệu form, tạo user mới nếu hợp lệ.
    Redirect về login sau khi đăng ký thành công.
    """
    # Nếu đã đăng nhập rồi → chuyển về trang chủ
    if current_user.is_authenticated:
        return redirect(url_for('documents.index'))

    form = RegisterForm()

    if form.validate_on_submit():
        # Mã hóa mật khẩu bằng bcrypt trước khi lưu vào DB
        password_bytes = form.password.data.encode('utf-8')
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))

        # Tạo user mới
        new_user = User(
            id=generate_uuid(),
            email=form.email.data.lower().strip(),          # Chuẩn hóa email về chữ thường
            password_hash=hashed_password.decode('utf-8'),  # Lưu dạng string
            full_name=form.full_name.data.strip(),
            role='USER'                                      # Mặc định là USER thường
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form, title='Đăng Ký')


# ============================================================
# Route: GET/POST /auth/login - Đăng nhập
# ============================================================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET:  Hiển thị form đăng nhập.
    POST: Kiểm tra tài khoản/mật khẩu, tạo session nếu đúng.
         Kiểm tra thêm: tài khoản có bị khóa (is_banned) không.
    """
    # Nếu đã đăng nhập rồi → chuyển về trang chủ
    if current_user.is_authenticated:
        return redirect(url_for('documents.index'))

    form = LoginForm()

    if form.validate_on_submit():
        # Tìm user theo email
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()

        if user is None:
            flash('Email không tồn tại trong hệ thống.', 'danger')
            return render_template('auth/login.html', form=form, title='Đăng Nhập')

        # Kiểm tra mật khẩu với bcrypt
        password_bytes = form.password.data.encode('utf-8')
        hash_bytes = user.password_hash.encode('utf-8')

        try:
            is_valid = bcrypt.checkpw(password_bytes, hash_bytes)
        except ValueError:
            is_valid = False

        if not is_valid:
            flash('Mật khẩu không đúng hoặc tài khoản chưa được mã hóa mật khẩu.', 'danger')
            return render_template('auth/login.html', form=form, title='Đăng Nhập')

        # Kiểm tra tài khoản có bị khóa không (Admin ban)
        if user.is_banned:
            flash('Tài khoản của bạn đã bị khóa. Vui lòng liên hệ Admin.', 'danger')
            return render_template('auth/login.html', form=form, title='Đăng Nhập')

        # Đăng nhập thành công - tạo session
        login_user(user, remember=form.remember.data)
        flash(f'Chào mừng {user.full_name}!', 'success')

        # Chuyển hướng về trang user muốn vào trước đó (nếu có)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('documents.index'))

    return render_template('auth/login.html', form=form, title='Đăng Nhập')


# ============================================================
# Route: GET /auth/logout - Đăng xuất
# Yêu cầu phải đang đăng nhập mới được dùng
# ============================================================
@auth_bp.route('/logout')
@login_required
def logout():
    """Xóa session đăng nhập và chuyển về trang chủ."""
    logout_user()
    flash('Bạn đã đăng xuất thành công.', 'info')
    return redirect(url_for('documents.index'))
