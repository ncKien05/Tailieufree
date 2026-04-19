# ============================================================
# app/routes/profile.py - Blueprint hồ sơ cá nhân
# Chứa: Xem hồ sơ, Chỉnh sửa, Đổi mật khẩu, Kho tài liệu
# URL prefix: /profile/
# Tất cả route đều yêu cầu đăng nhập
# ============================================================

import bcrypt
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort)
from flask_login import login_required, current_user
from .. import db
from ..models import Document, User
from ..forms import EditProfileForm, ChangePasswordForm, EditDocTitleForm
from ..utils import save_avatar

# Tạo Blueprint với tên 'profile'
profile_bp = Blueprint('profile', __name__)


# ============================================================
# Route: GET /profile/ và /profile/<user_id> - Xem hồ sơ
# ============================================================
@profile_bp.route('/')
@profile_bp.route('/<string:user_id>')
@login_required
def profile(user_id=None):
    """
    Hiển thị trang hồ sơ. 
    Nếu không có user_id -> xem trang của mình.
    """
    from ..models import Bookmark, DownloadHistory

    if user_id is None:
        user_id = current_user.id
        
    user = User.query.get_or_404(user_id)
    is_owner = (current_user.id == user.id)

    # 1. Danh sách tài liệu đã upload
    my_docs = (Document.query
               .filter_by(uploader_id=user.id)
               .order_by(Document.created_at.desc())
               .all())

    # 2. Danh sách Bookmark (chỉ chủ sở hữu mới xem được)
    bookmarked_docs = []
    # 3. Lịch sử tải xuống (chỉ chủ sở hữu mới xem được)
    downloaded_docs = []

    if is_owner:
        bookmarks = Bookmark.query.filter_by(user_id=user.id).order_by(Bookmark.created_at.desc()).all()
        bookmarked_docs = [b.document for b in bookmarks if b.document is not None]

        downloads = DownloadHistory.query.filter_by(user_id=user.id).order_by(DownloadHistory.downloaded_at.desc()).all()
        downloaded_docs = [d.document_ref for d in downloads if d.document_ref is not None]

    return render_template('profile/profile.html',
                           user=user,
                           documents=my_docs,
                           bookmarked_docs=bookmarked_docs,
                           downloaded_docs=downloaded_docs,
                           is_owner=is_owner,
                           title=f'Hồ Sơ Của {user.full_name}')


# ============================================================
# Route: GET/POST /profile/edit - Chỉnh sửa thông tin cá nhân
# ============================================================
@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    GET:  Hiển thị form với thông tin hiện tại của user.
    POST: Cập nhật thông tin (tên, trường, ngành, bio, avatar).
          Nếu có upload avatar mới → lưu ảnh, resize về 200x200px.
    """
    form = EditProfileForm(obj=current_user)  # Pre-fill form từ dữ liệu user hiện tại

    if form.validate_on_submit():
        # Cập nhật thông tin cơ bản
        current_user.full_name = form.full_name.data.strip()
        current_user.school = form.school.data.strip() if form.school.data else None
        current_user.major = form.major.data.strip() if form.major.data else None
        current_user.bio = form.bio.data.strip() if form.bio.data else None

        # Xử lý avatar nếu user có upload ảnh mới
        if form.avatar.data:
            avatar_url = save_avatar(form.avatar.data, current_user.id)
            current_user.avatar_url = avatar_url

        db.session.commit()
        flash('Cập nhật hồ sơ thành công!', 'success')
        return redirect(url_for('profile.profile'))

    return render_template('profile/edit.html', form=form, title='Chỉnh Sửa Hồ Sơ')


# ============================================================
# Route: GET/POST /profile/change-password - Đổi mật khẩu
# ============================================================
@profile_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Cho phép user đổi mật khẩu:
    1. Kiểm tra mật khẩu hiện tại bằng bcrypt
    2. Nếu đúng → mã hóa mật khẩu mới và lưu vào DB
    """
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # Kiểm tra mật khẩu hiện tại
        current_pw_bytes = form.current_password.data.encode('utf-8')
        stored_hash_bytes = current_user.password_hash.encode('utf-8')

        if not bcrypt.checkpw(current_pw_bytes, stored_hash_bytes):
            flash('Mật khẩu hiện tại không đúng.', 'danger')
            return render_template('profile/change_password.html',
                                   form=form, title='Đổi Mật Khẩu')

        # Mã hóa và lưu mật khẩu mới
        new_pw_bytes = form.new_password.data.encode('utf-8')
        new_hash = bcrypt.hashpw(new_pw_bytes, bcrypt.gensalt(rounds=12))
        current_user.password_hash = new_hash.decode('utf-8')

        db.session.commit()
        flash('Đổi mật khẩu thành công!', 'success')
        return redirect(url_for('profile.profile'))

    return render_template('profile/change_password.html',
                           form=form, title='Đổi Mật Khẩu')


# ============================================================
# Route: GET /profile/documents - Kho tài liệu cá nhân
# ============================================================
@profile_bp.route('/documents')
@login_required
def my_documents():
    """
    Hiển thị danh sách tất cả tài liệu user đã upload,
    bao gồm trạng thái: PENDING / APPROVED / REJECTED.
    """
    page = request.args.get('page', 1, type=int)
    docs = (Document.query
            .filter_by(uploader_id=current_user.id)
            .order_by(Document.created_at.desc())
            .paginate(page=page, per_page=10, error_out=False))

    return render_template('profile/my_documents.html',
                           documents=docs,
                           title='Tài Liệu Của Tôi')


# ============================================================
# Route: GET/POST /profile/documents/<doc_id>/edit - Sửa tài liệu
# Chỉ chủ sở hữu mới được sửa tài liệu của chính mình
# ============================================================
@profile_bp.route('/documents/<string:doc_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_document(doc_id):
    """
    Cho phép user chỉnh sửa tiêu đề và mô tả của tài liệu.
    Kiểm tra quyền: chỉ người đã upload mới được sửa.
    Sau khi sửa → tài liệu về lại trạng thái PENDING chờ duyệt lại.
    """
    doc = Document.query.get_or_404(doc_id)

    # Kiểm tra quyền sở hữu - chỉ chủ tài liệu mới được sửa
    if doc.uploader_id != current_user.id:
        abort(403)

    form = EditDocTitleForm(obj=doc)  # Pre-fill form từ dữ liệu tài liệu

    if form.validate_on_submit():
        doc.title = form.title.data.strip()
        doc.description = form.description.data
        doc.status = 'PENDING'  # Reset về PENDING để admin duyệt lại sau khi sửa

        db.session.commit()
        flash('Cập nhật tài liệu thành công. Tài liệu đang chờ duyệt lại.', 'success')
        return redirect(url_for('profile.my_documents'))

    return render_template('profile/edit_document.html',
                           form=form, doc=doc, title='Sửa Tài Liệu')


# ============================================================
# Route: POST /profile/documents/<doc_id>/delete - Xóa tài liệu
# Chỉ chủ sở hữu mới được xóa tài liệu của chính mình
# ============================================================
@profile_bp.route('/documents/<string:doc_id>/delete', methods=['POST'])
@login_required
def delete_document(doc_id):
    """
    Xóa tài liệu khỏi database.
    Kiểm tra quyền: chỉ người đã upload mới được xóa.
    Lưu ý: File thực tế trên disk không bị xóa (có thể backup sau).
    """
    doc = Document.query.get_or_404(doc_id)

    # Kiểm tra quyền sở hữu
    if doc.uploader_id != current_user.id:
        abort(403)

    doc_title = doc.title
    db.session.delete(doc)
    db.session.commit()

    flash(f'Đã xóa tài liệu "{doc_title}".', 'success')
    return redirect(url_for('profile.my_documents'))
