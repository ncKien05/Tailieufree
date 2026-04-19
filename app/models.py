# ============================================================
# app/models.py - Định nghĩa các Model SQLAlchemy
# Mỗi class ánh xạ tương ứng với một bảng trong database
# ============================================================

from datetime import datetime
from flask_login import UserMixin
from . import db   # Import db instance từ app/__init__.py


# ============================================================
# Model: User - Bảng người dùng
# Kế thừa UserMixin để tích hợp với Flask-Login
# ============================================================
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    # Các cột của bảng
    id = db.Column(db.String(36), primary_key=True)                         # UUID
    email = db.Column(db.String(255), unique=True, nullable=False)          # Email đăng nhập
    password_hash = db.Column(db.String(255), nullable=False)               # Mật khẩu đã mã hoá
    full_name = db.Column(db.String(100))                                   # Tên hiển thị
    avatar_url = db.Column(db.String(255))                                  # Ảnh đại diện
    bio = db.Column(db.Text)                                                # Giới thiệu bản thân
    school = db.Column(db.String(150))                                      # Trường học
    major = db.Column(db.String(150))                                       # Ngành học
    role = db.Column(db.Enum('USER', 'MOD', 'ADMIN'), default='USER')      # Phân quyền
    is_banned = db.Column(db.Boolean, default=False)                        # Trạng thái bị khóa
    reputation_points = db.Column(db.Integer, default=0)                    # Điểm uy tín
    created_at = db.Column(db.DateTime, default=datetime.utcnow)            # Ngày tạo

    # Quan hệ: 1 user có nhiều tài liệu (one-to-many)
    documents = db.relationship('Document', backref='uploader', lazy=True,
                                foreign_keys='Document.uploader_id')

    # Quan hệ mở rộng
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    ratings = db.relationship('Rating', backref='reviewer', lazy=True)
    bookmarks = db.relationship('Bookmark', backref='user', lazy=True)
    download_history = db.relationship('DownloadHistory', backref='user', lazy=True)

    # --- Các helper method ---

    def is_admin(self):
        """Kiểm tra user có phải Admin không."""
        return self.role == 'ADMIN'

    def is_mod(self):
        """Kiểm tra user có phải Moderator không."""
        return self.role in ('MOD', 'ADMIN')

    def __repr__(self):
        return f'<User {self.email}>'


# ============================================================
# Model: Category - Bảng danh mục (môn học / loại tài liệu)
# ============================================================
class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)                        # Tên danh mục
    type = db.Column(db.Enum('DOCUMENT', 'SUBJECT'), nullable=False)       # Loại danh mục

    # Quan hệ: 1 danh mục có nhiều tài liệu
    documents = db.relationship('Document', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


# ============================================================
# Model: Document - Bảng tài liệu
# ============================================================
class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.String(36), primary_key=True)                         # UUID
    uploader_id = db.Column(db.String(36), db.ForeignKey('users.id',
                            ondelete='SET NULL'), nullable=True)            # FK → users
    title = db.Column(db.String(255), nullable=False)                       # Tên tài liệu
    description = db.Column(db.Text)                                        # Mô tả
    file_url = db.Column(db.String(255), nullable=False)                    # Đường dẫn file
    file_format = db.Column(db.String(10))                                  # Định dạng: PDF/DOCX/PPTX
    school_tag = db.Column(db.String(150))                                  # Tag trường học
    academic_year = db.Column(db.String(20))                                # Năm học
    category_id = db.Column(db.Integer, db.ForeignKey('category.id',
                            ondelete='SET NULL'), nullable=True)            # FK → category
    status = db.Column(db.Enum('PENDING', 'APPROVED', 'REJECTED'),
                       default='PENDING')                                   # Trạng thái duyệt
    download_count = db.Column(db.Integer, default=0)                      # Số lượt tải
    view_count = db.Column(db.Integer, default=0)                          # Số lượt xem
    created_at = db.Column(db.DateTime, default=datetime.utcnow)            # Ngày upload

    # Quan hệ mở rộng: 1 tài liệu có nhiều đánh giá, comment, bookmark, lịch sử tải
    ratings = db.relationship('Rating', backref='document', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='document', lazy=True, cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='document', lazy=True, cascade='all, delete-orphan')
    download_history = db.relationship('DownloadHistory', backref='document_ref', lazy=True, cascade='all, delete-orphan')

    def is_approved(self):
        """Kiểm tra tài liệu đã được duyệt chưa."""
        return self.status == 'APPROVED'

    def __repr__(self):
        return f'<Document {self.title}>'


# ============================================================
# Model: Post - Bài viết Blog
# ============================================================
class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False) # MEDIUMTEXT
    tags = db.Column(db.String(255))
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

# ============================================================
# Model: Comment - Bình luận
# ============================================================
class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.String(36), db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=True)
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============================================================
# Model: Rating - Đánh giá tài liệu
# ============================================================
class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    doc_id = db.Column(db.String(36), db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    star_value = db.Column(db.SmallInteger, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============================================================
# Model: Bookmark - Lưu tài liệu
# ============================================================
class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    doc_id = db.Column(db.String(36), db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============================================================
# Model: DownloadHistory - Lịch sử tải về
# ============================================================
class DownloadHistory(db.Model):
    __tablename__ = 'download_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow)
