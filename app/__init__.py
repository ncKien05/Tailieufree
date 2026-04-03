from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # Tải các biến từ file .env
    load_dotenv()

    app = Flask(__name__)

    # Cấu hình từ môi trường
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.rootpath, '../uploads')

    # Liên kết database và login manager vào app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Trang chuyển hướng nếu chưa đăng nhập

    # Đăng ký Blueprints
    from .routes.auth import auth_bp
    from .routes.documents import doc_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(doc_bp, url_prefix='/')

    return app