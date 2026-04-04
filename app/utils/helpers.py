# ============================================================
# app/utils/helpers.py - Các hàm tiện ích dùng chung
# ============================================================

import os
import uuid
from functools import wraps
from flask import abort, current_app
from flask_login import current_user
from PIL import Image
from werkzeug.utils import secure_filename

# --- Định nghĩa các định dạng file được phép upload ---
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'docx', 'pptx'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


# ============================================================
# Hàm: Tạo UUID ngẫu nhiên (dùng làm ID cho user/document)
# ============================================================
def generate_uuid():
    """Tạo một chuỗi UUID4 ngẫu nhiên."""
    return str(uuid.uuid4())


# ============================================================
# Hàm: Kiểm tra phần mở rộng file có hợp lệ không
# ============================================================
def allowed_file(filename, file_type='document'):
    """
    Kiểm tra xem file có phần mở rộng hợp lệ không.
    file_type: 'document' hoặc 'image'
    """
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == 'image':
        return ext in ALLOWED_IMAGE_EXTENSIONS
    return ext in ALLOWED_DOCUMENT_EXTENSIONS


# ============================================================
# Hàm: Lưu file tài liệu (PDF/DOCX/PPTX) lên server
# Trả về: đường dẫn tương đối để lưu vào database
# ============================================================
def save_uploaded_file(file_obj):
    """
    Lưu file tài liệu vào thư mục uploads/documents/.
    Đặt tên file theo UUID để tránh trùng lặp.
    Trả về tuple: (file_url_relative, file_format)
    """
    # Làm sạch tên file để tránh path traversal attack
    original_filename = secure_filename(file_obj.filename)
    extension = original_filename.rsplit('.', 1)[1].lower()

    # Tạo tên file mới bằng UUID để tránh trùng lặp
    new_filename = f"{generate_uuid()}.{extension}"

    # Tạo thư mục lưu tài liệu nếu chưa có
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents')
    os.makedirs(upload_dir, exist_ok=True)

    # Lưu file
    file_path = os.path.join(upload_dir, new_filename)
    file_obj.save(file_path)

    # Trả về đường dẫn tương đối để lưu vào DB
    relative_url = f"documents/{new_filename}"
    return relative_url, extension.upper()


# ============================================================
# Hàm: Lưu ảnh đại diện (avatar) và resize về 200x200px
# ============================================================
def save_avatar(file_obj, user_id):
    """
    Lưu ảnh đại diện vào uploads/avatars/, resize về 200x200px.
    Trả về: đường dẫn tương đối của ảnh mới.
    """
    original_filename = secure_filename(file_obj.filename)
    extension = original_filename.rsplit('.', 1)[1].lower()

    # Đặt tên file theo user_id để dễ quản lý
    new_filename = f"{user_id}.{extension}"

    # Tạo thư mục lưu avatar nếu chưa có
    avatar_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
    os.makedirs(avatar_dir, exist_ok=True)

    file_path = os.path.join(avatar_dir, new_filename)

    # Resize ảnh về kích thước chuẩn bằng Pillow
    img = Image.open(file_obj)
    img = img.convert('RGB')            # Đảm bảo ảnh là RGB (xử lý ảnh có transparency)
    img.thumbnail((200, 200))           # Resize giữ tỉ lệ, tối đa 200x200
    img.save(file_path)

    return f"avatars/{new_filename}"


# ============================================================
# Decorator: Yêu cầu quyền Admin
# Dùng để bảo vệ các route trong admin blueprint
# ============================================================
def admin_required(f):
    """
    Decorator bảo vệ route chỉ dành cho Admin.
    Nếu user không phải admin → trả về lỗi 403 Forbidden.
    Dùng: @admin_required ngay dưới @login_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)  # Chưa đăng nhập
        if not current_user.is_admin():
            abort(403)  # Không có quyền
        return f(*args, **kwargs)
    return decorated_function


# ============================================================
# Decorator: Yêu cầu quyền Moderator hoặc Admin
# ============================================================
def mod_required(f):
    """
    Decorator bảo vệ route dành cho Mod/Admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_mod():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
