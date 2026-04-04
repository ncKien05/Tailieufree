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

    # Quan hệ: 1 user có nhiều đánh giá (one-to-many)
    reviews = db.relationship('CommunityReview', backref='reviewer', lazy=True)

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
    downloads_count = db.Column(db.Integer, default=0)                      # Số lượt tải
    created_at = db.Column(db.DateTime, default=datetime.utcnow)            # Ngày upload

    # Quan hệ: 1 tài liệu có nhiều đánh giá
    reviews = db.relationship('CommunityReview', backref='document',
                              lazy=True, cascade='all, delete-orphan')

    def is_approved(self):
        """Kiểm tra tài liệu đã được duyệt chưa."""
        return self.status == 'APPROVED'

    def __repr__(self):
        return f'<Document {self.title}>'


# ============================================================
# Model: CommunityReview - Bảng đánh giá cộng đồng
# ============================================================
class CommunityReview(db.Model):
    __tablename__ = 'community_review'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id',
                            ondelete='CASCADE'), nullable=False)            # FK → documents
    user_id = db.Column(db.String(36), db.ForeignKey('users.id',
                        ondelete='CASCADE'), nullable=False)                # FK → users
    rating = db.Column(db.SmallInteger, nullable=False)                     # Điểm 1-5 sao
    comment = db.Column(db.Text)                                            # Nội dung nhận xét
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review doc={self.document_id} rating={self.rating}>'
