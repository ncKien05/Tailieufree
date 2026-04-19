# ============================================================
# app/__init__.py - Application Factory
# SỬA: Thêm CSRFProtect để {{ csrf_token() }} hoạt động trong template
# SỬA: Thêm Flask CLI commands: create-admin, init-db
# SỬA: Dùng CLI command thay vì db.create_all() trong create_app()
#       để tránh crash khi MySQL chưa sẵn sàng
# ============================================================

from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect   # THÊM MỚI: bảo vệ CSRF toàn app
from dotenv import load_dotenv
import os

# Khởi tạo extensions (chưa gắn vào app, sẽ gắn trong create_app)
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()    # THÊM MỚI: instance CSRFProtect


def create_app():
    """Application Factory - tạo và cấu hình Flask app."""
    load_dotenv()

    app = Flask(__name__)

    # --------------------------------------------------------
    # Cấu hình từ biến môi trường
    # --------------------------------------------------------
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, '..', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

    # THÊM MỚI: pool_pre_ping kiểm tra kết nối trước mỗi query,
    # tránh lỗi "MySQL connection lost" sau thời gian dài không dùng
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,   # Tái sử dụng connection sau 5 phút
    }

    # --------------------------------------------------------
    # Liên kết các extensions vào app
    # --------------------------------------------------------
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)  # Kích hoạt CSRF → hàm csrf_token() hoạt động trong template

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để tiếp tục.'
    login_manager.login_message_category = 'warning'

    # --------------------------------------------------------
    # User loader - Flask-Login dùng để load user từ session
    # --------------------------------------------------------
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        """Load user từ database dựa trên user_id lưu trong session."""
        return User.query.get(user_id)

    # --------------------------------------------------------
    # Đăng ký Blueprints
    # --------------------------------------------------------
    from .routes.auth import auth_bp
    from .routes.documents import doc_bp
    from .routes.profile import profile_bp
    from .routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(doc_bp, url_prefix='/')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # --------------------------------------------------------
    # THÊM MỚI: CLI command 'init-db' - tạo tất cả bảng từ models
    # Tách ra CLI command thay vì chạy trong create_app() để tránh
    # crash khi MySQL chưa sẵn sàng lúc app khởi động
    # Dùng: docker-compose exec web flask init-db
    # --------------------------------------------------------
    @app.cli.command('init-db')
    def init_db():
        """Tạo tất cả bảng trong database từ SQLAlchemy models."""
        from . import models as _models  # noqa: F401 - import để SQLAlchemy nhận diện models
        db.create_all()
        print('[✓] Đã tạo tất cả bảng trong database.')

    # --------------------------------------------------------
    # THÊM MỚI: CLI command 'create-admin' - tạo tài khoản Admin
    # Lý do dùng CLI thay vì seed.sql: bcrypt hash phải được tạo
    # động bởi thư viện Python, không thể hardcode trong SQL
    # Dùng: docker-compose exec web flask create-admin
    # --------------------------------------------------------
    @app.cli.command('create-admin')
    def create_admin():
        """Tạo tài khoản Admin mặc định."""
        import bcrypt
        from .utils import generate_uuid

        admin_email = 'admin@tailieufree.vn'
        admin_password = 'Admin@123'

        # Đảm bảo bảng users tồn tại trước (trong trường hợp chưa init-db)
        from . import models as _models  # noqa: F401
        db.create_all()

        # Kiểm tra admin đã tồn tại chưa
        existing = User.query.filter_by(email=admin_email).first()
        if existing:
            print(f'[!] Admin đã tồn tại: {admin_email}')
            return

        # Hash mật khẩu bằng bcrypt
        hashed = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt(12))

        admin = User(
            id=generate_uuid(),
            email=admin_email,
            password_hash=hashed.decode('utf-8'),
            full_name='Quản Trị Viên',
            role='ADMIN',
            bio='Tài khoản quản trị hệ thống TailLieuFree.',
            is_banned=False
        )
        db.session.add(admin)
        db.session.commit()
        print(f'[✓] Đã tạo Admin: {admin_email} | Mật khẩu: {admin_password}')

    # --------------------------------------------------------
    # Xử lý lỗi toàn cục
    # --------------------------------------------------------
    register_error_handlers(app)

    # --------------------------------------------------------
    # Xử lý phục vụ file từ thư mục Upload (Ảnh Avatar bìa)
    # --------------------------------------------------------
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app


def register_error_handlers(app):
    """Đăng ký các trang lỗi tùy chỉnh."""
    from flask import render_template

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def file_too_large(e):
        return render_template('errors/413.html'), 413