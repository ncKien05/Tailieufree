# ============================================================
# app/routes/admin.py - Blueprint Quản trị hệ thống
# Chứa: Dashboard, Kiểm duyệt tài liệu, Quản lý user, Danh mục
# URL prefix: /admin/
# Tất cả route đều yêu cầu quyền ADMIN
# ============================================================

from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request)
from flask_login import login_required
from .. import db
from ..models import User, Document, Category
from ..forms import CategoryForm
from ..utils import admin_required

# Tạo Blueprint với tên 'admin'
admin_bp = Blueprint('admin', __name__)


# ============================================================
# Route: GET /admin/ - Trang Dashboard tổng quan
# ============================================================
@admin_bp.route('/')
@login_required
@admin_required  # Custom decorator: kiểm tra role == 'ADMIN'
def dashboard():
    """
    Trang tổng quan hệ thống dành cho Admin.
    Hiển thị các thống kê nhanh:
    - Tổng số user
    - Tổng số tài liệu (phân theo trạng thái)
    - Số tài liệu đang chờ duyệt (cần xử lý ngay)
    """
    # Thống kê nhanh bằng COUNT()
    total_users = User.query.count()
    total_docs = Document.query.count()
    pending_docs = Document.query.filter_by(status='PENDING').count()
    approved_docs = Document.query.filter_by(status='APPROVED').count()
    rejected_docs = Document.query.filter_by(status='REJECTED').count()
    banned_users = User.query.filter_by(is_banned=True).count()

    # 5 tài liệu mới nhất đang chờ duyệt
    recent_pending = (Document.query
                      .filter_by(status='PENDING')
                      .order_by(Document.created_at.desc())
                      .limit(5).all())

    stats = {
        'total_users': total_users,
        'total_docs': total_docs,
        'pending_docs': pending_docs,
        'approved_docs': approved_docs,
        'rejected_docs': rejected_docs,
        'banned_users': banned_users
    }

    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_pending=recent_pending,
                           title='Admin Dashboard')


# ============================================================
# Route: GET /admin/documents - Danh sách & kiểm duyệt tài liệu
# ============================================================
@admin_bp.route('/documents')
@login_required
@admin_required
def manage_documents():
    """
    Hiển thị danh sách TẤT CẢ tài liệu trong hệ thống.
    Có thể lọc theo trạng thái: ALL / PENDING / APPROVED / REJECTED
    """
    status_filter = request.args.get('status', 'PENDING')  # Mặc định xem PENDING trước
    page = request.args.get('page', 1, type=int)

    query = Document.query
    if status_filter in ('PENDING', 'APPROVED', 'REJECTED'):
        query = query.filter_by(status=status_filter)

    documents = query.order_by(Document.created_at.desc())\
                     .paginate(page=page, per_page=15, error_out=False)

    return render_template('admin/documents.html',
                           documents=documents,
                           status_filter=status_filter,
                           title='Quản Lý Tài Liệu')


# ============================================================
# Route: POST /admin/documents/<doc_id>/approve - Duyệt tài liệu
# ============================================================
@admin_bp.route('/documents/<string:doc_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_document(doc_id):
    """Duyệt tài liệu: Đổi status từ PENDING → APPROVED."""
    doc = Document.query.get_or_404(doc_id)
    doc.status = 'APPROVED'
    db.session.commit()
    flash(f'Đã duyệt tài liệu: "{doc.title}"', 'success')
    return redirect(url_for('admin.manage_documents', status='PENDING'))


# ============================================================
# Route: POST /admin/documents/<doc_id>/reject - Từ chối tài liệu
# ============================================================
@admin_bp.route('/documents/<string:doc_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_document(doc_id):
    """
    Từ chối/ẩn tài liệu: Đổi status → REJECTED.
    Tài liệu sẽ không hiển thị trên trang chủ nhưng còn trong DB.
    """
    doc = Document.query.get_or_404(doc_id)
    doc.status = 'REJECTED'
    db.session.commit()
    flash(f'Đã từ chối tài liệu: "{doc.title}"', 'warning')
    return redirect(url_for('admin.manage_documents', status='PENDING'))


# ============================================================
# Route: POST /admin/documents/<doc_id>/delete - Xóa hẳn tài liệu
# ============================================================
@admin_bp.route('/documents/<string:doc_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_document(doc_id):
    """
    Xóa tài liệu hoàn toàn khỏi database (bao gồm cả reviews).
    Dùng khi tài liệu vi phạm nghiêm trọng.
    """
    doc = Document.query.get_or_404(doc_id)
    doc_title = doc.title
    db.session.delete(doc)
    db.session.commit()
    flash(f'Đã xóa vĩnh viễn tài liệu: "{doc_title}"', 'danger')
    return redirect(url_for('admin.manage_documents'))


# ============================================================
# Route: GET /admin/users - Danh sách người dùng
# ============================================================
@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """
    Hiển thị danh sách tất cả người dùng.
    Có thể lọc: tất cả / bị khóa.
    Hiển thị: email, họ tên, role, trạng thái, số tài liệu đã upload.
    """
    show_banned = request.args.get('banned', '0') == '1'
    page = request.args.get('page', 1, type=int)

    query = User.query
    if show_banned:
        query = query.filter_by(is_banned=True)

    users = query.order_by(User.created_at.desc())\
                 .paginate(page=page, per_page=20, error_out=False)

    return render_template('admin/users.html',
                           users=users,
                           show_banned=show_banned,
                           title='Quản Lý Người Dùng')


# ============================================================
# Route: POST /admin/users/<user_id>/ban - Khóa tài khoản
# ============================================================
@admin_bp.route('/users/<string:user_id>/ban', methods=['POST'])
@login_required
@admin_required
def ban_user(user_id):
    """
    Khóa tài khoản người dùng (is_banned = True).
    User bị khóa sẽ không thể đăng nhập.
    Admin không thể tự khóa chính mình.
    """
    from flask_login import current_user

    user = User.query.get_or_404(user_id)

    # Ngăn admin tự khóa chính mình
    if user.id == current_user.id:
        flash('Bạn không thể tự khóa tài khoản của chính mình!', 'danger')
        return redirect(url_for('admin.manage_users'))

    user.is_banned = True
    db.session.commit()
    flash(f'Đã khóa tài khoản: {user.email}', 'warning')
    return redirect(url_for('admin.manage_users'))


# ============================================================
# Route: POST /admin/users/<user_id>/unban - Mở khóa tài khoản
# ============================================================
@admin_bp.route('/users/<string:user_id>/unban', methods=['POST'])
@login_required
@admin_required
def unban_user(user_id):
    """Mở khóa tài khoản (is_banned = False)."""
    user = User.query.get_or_404(user_id)
    user.is_banned = False
    db.session.commit()
    flash(f'Đã mở khóa tài khoản: {user.email}', 'success')
    return redirect(url_for('admin.manage_users'))


# ============================================================
# Route: GET /admin/categories - Quản lý danh mục
# ============================================================
@admin_bp.route('/categories')
@login_required
@admin_required
def manage_categories():
    """
    Hiển thị tất cả danh mục môn học/loại tài liệu.
    Kèm form để thêm danh mục mới.
    """
    categories = Category.query.order_by(Category.id.asc()).all()  # Sắp xếp theo ID tăng dần
    form = CategoryForm()  # Form thêm danh mục mới
    return render_template('admin/categories.html',
                           categories=categories,
                           form=form,
                           title='Quản Lý Danh Mục')


# ============================================================
# Route: POST /admin/categories/add - Thêm danh mục mới
# ============================================================
@admin_bp.route('/categories/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    """Thêm danh mục môn học hoặc loại tài liệu mới."""
    form = CategoryForm()

    if form.validate_on_submit():
        new_cat = Category(name=form.name.data.strip(), type=form.type.data)
        db.session.add(new_cat)
        db.session.commit()
        flash(f'Đã thêm danh mục: "{new_cat.name}"', 'success')
    else:
        flash('Dữ liệu không hợp lệ.', 'danger')

    return redirect(url_for('admin.manage_categories'))


# ============================================================
# Route: POST /admin/categories/<cat_id>/edit - Sửa danh mục
# ============================================================
@admin_bp.route('/categories/<int:cat_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_category(cat_id):
    """Cập nhật tên và loại của danh mục."""
    cat = Category.query.get_or_404(cat_id)
    new_name = request.form.get('name', '').strip()
    new_type = request.form.get('type', '').strip()

    if not new_name:
        flash('Tên danh mục không được để trống.', 'danger')
        return redirect(url_for('admin.manage_categories'))

    if new_type not in ('SUBJECT', 'DOCUMENT'):
        flash('Loại danh mục không hợp lệ.', 'danger')
        return redirect(url_for('admin.manage_categories'))

    cat.name = new_name
    cat.type = new_type
    db.session.commit()
    flash(f'Đã cập nhật danh mục: "{cat.name}"', 'success')
    return redirect(url_for('admin.manage_categories'))


# ============================================================
# Route: POST /admin/categories/<cat_id>/delete - Xóa danh mục
# ============================================================
@admin_bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(cat_id):
    """
    Xóa danh mục.
    Tài liệu thuộc danh mục này sẽ có category_id = NULL (ON DELETE SET NULL).
    """
    cat = Category.query.get_or_404(cat_id)
    cat_name = cat.name
    db.session.delete(cat)
    db.session.commit()
    flash(f'Đã xóa danh mục: "{cat_name}"', 'danger')
    return redirect(url_for('admin.manage_categories'))
