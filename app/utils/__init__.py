# ============================================================
# app/utils/__init__.py
# Package utils - chứa các hàm tiện ích dùng chung toàn app
# ============================================================

# Export các hàm chính để import tiện hơn
from .helpers import (
    save_uploaded_file,
    save_avatar,
    allowed_file,
    admin_required,
    generate_uuid
)
