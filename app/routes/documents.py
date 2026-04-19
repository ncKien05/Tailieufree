# ============================================================
# app/routes/documents.py - Blueprint quản lý tài liệu
# Chứa: Trang chủ, Tìm kiếm, Upload, Xem chi tiết, Tải xuống
# URL prefix: /
# ============================================================

import os
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, send_from_directory, abort, current_app)
from flask_login import login_required, current_user
from .. import db
from ..models import Document, Category, Rating, Comment, DownloadHistory
from ..forms import UploadDocForm
from ..utils import save_uploaded_file, generate_uuid

# Tạo Blueprint với tên 'documents'
doc_bp = Blueprint('documents', __name__)


# ============================================================
# Route: GET / - Trang chủ, hiển thị danh sách tài liệu
# Khách vãng lai được phép truy cập (không cần đăng nhập)
# ============================================================
@doc_bp.route('/')
def index():
    """
    Trang chủ: Hiển thị tài liệu đã được duyệt (status=APPROVED).
    Hỗ trợ phân trang: mỗi trang 12 tài liệu.
    Khách vãng lai được phép xem - không cần đăng nhập.
    """
    page = request.args.get('page', 1, type=int)

    # Query chỉ lấy tài liệu đã được duyệt, sắp xếp mới nhất trước
    documents = (Document.query
                 .filter_by(status='APPROVED')
                 .order_by(Document.created_at.desc())
                 .paginate(page=page, per_page=12, error_out=False))

    # Lấy tất cả danh mục để hiển thị bộ lọc
    categories = Category.query.all()

    return render_template('documents/index.html',
                           documents=documents,
                           categories=categories,
                           title='Trang Chủ - TailLieuFree')


# ============================================================
# Route: GET /search - Tìm kiếm và lọc tài liệu
# Khách vãng lai được phép tìm kiếm
# ============================================================
@doc_bp.route('/search')
def search():
    """
    Tìm kiếm tài liệu theo:
    - Từ khóa trong tiêu đề (q)
    - Danh mục/môn học (category_id)
    - Tag trường (school_tag)
    - Năm học (academic_year)
    """
    # Lấy tham số tìm kiếm từ URL query string
    keyword = request.args.get('q', '').strip()
    category_id = request.args.get('category_id', type=int)
    school_tag = request.args.get('school_tag', '').strip()
    academic_year = request.args.get('academic_year', '').strip()
    page = request.args.get('page', 1, type=int)

    # Bắt đầu query, chỉ lấy tài liệu đã duyệt
    query = Document.query.filter_by(status='APPROVED')

    # Áp dụng bộ lọc nếu có tham số
    if keyword:
        query = query.filter(Document.title.ilike(f'%{keyword}%'))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if school_tag:
        query = query.filter(Document.school_tag.ilike(f'%{school_tag}%'))
    if academic_year:
        query = query.filter_by(academic_year=academic_year)

    documents = query.order_by(Document.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False)

    categories = Category.query.all()

    return render_template('documents/index.html',
                           documents=documents,
                           categories=categories,
                           keyword=keyword,
                           selected_category=category_id,
                           title=f'Tìm kiếm: {keyword}')


# ============================================================
# Route: GET/POST /upload - Tải tài liệu lên
# Chỉ thành viên đã đăng nhập mới được upload
# ============================================================
@doc_bp.route('/upload', methods=['GET', 'POST'])
@login_required   # Decorator: Chuyển về login nếu chưa đăng nhập
def upload():
    """
    GET:  Hiển thị form upload tài liệu.
    POST: Xử lý file upload + thông tin form.
          - Lưu file vào thư mục uploads/documents/
          - Tạo bản ghi Document với status='PENDING' (chờ duyệt)
          - Admin sẽ duyệt sau trong Admin Dashboard
    """
    form = UploadDocForm()

    # Populate dropdown danh mục từ database
    categories = Category.query.all()
    form.category_id.choices = [(0, '-- Chọn danh mục --')] + \
                                [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        try:
            # Lưu file lên server, nhận về đường dẫn và định dạng
            file_url, file_format = save_uploaded_file(form.document_file.data)

            # Tạo bản ghi tài liệu trong database
            new_doc = Document(
                id=generate_uuid(),
                uploader_id=current_user.id,
                title=form.title.data.strip(),
                description=form.description.data,
                file_url=file_url,
                file_format=file_format,
                school_tag=form.school_tag.data.strip() if form.school_tag.data else None,
                academic_year=form.academic_year.data.strip() if form.academic_year.data else None,
                category_id=form.category_id.data if form.category_id.data != 0 else None,
                status='PENDING'    # Mặc định chờ Admin duyệt
            )

            db.session.add(new_doc)
            db.session.commit()

            flash('Tải lên thành công! Tài liệu đang chờ Admin kiểm duyệt.', 'success')
            return redirect(url_for('profile.my_documents'))

        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra khi tải lên: {str(e)}', 'danger')

    return render_template('documents/upload.html', form=form, title='Tải Tài Liệu Lên')


# ============================================================
# Route: GET /documents/<doc_id> - Xem chi tiết tài liệu
# Khách vãng lai được phép xem
# ============================================================
@doc_bp.route('/documents/<string:doc_id>')
def detail(doc_id):
    """Hiển thị trang chi tiết tài liệu kèm form đánh giá."""
    doc = Document.query.get_or_404(doc_id)

    is_owner = current_user.is_authenticated and current_user.id == doc.uploader_id
    is_admin = current_user.is_authenticated and current_user.is_admin()

    if doc.status != 'APPROVED' and not is_owner and not is_admin:
        abort(404)

    # Lấy danh sách rating và comment riêng rẽ
    ratings = Rating.query.filter_by(doc_id=doc_id).order_by(Rating.created_at.desc()).all()
    comments = Comment.query.filter_by(document_id=doc_id).order_by(Comment.created_at.desc()).all()

    # Kiểm tra user hiện tại đã đánh giá chưa
    user_review = None
    can_review  = False
    review_form = None
    if current_user.is_authenticated:
        user_review = Rating.query.filter_by(
            doc_id=doc_id,
            user_id=current_user.id
        ).first() # gán tạm user_review làm rating để template dùng đỡ crash
        # Có thể đánh giá: đã đăng nhập, không phải chủ tài liệu,
        # chưa đánh giá, tài liệu APPROVED
        can_review = (not is_owner
                      and user_review is None
                      and doc.status == 'APPROVED')
        review_form = can_review  # True/False — template dùng để hiển form HTML thuần

    return render_template('documents/detail.html',
                           doc=doc,
                           ratings=ratings,
                           comments=comments,
                           is_owner=is_owner,
                           review_form=review_form,
                           user_review=user_review,
                           can_review=can_review,
                           title=doc.title)


# ============================================================
# Route: POST /documents/<doc_id>/review - Gửi đánh giá
# ============================================================
@doc_bp.route('/documents/<string:doc_id>/review', methods=['POST'])
@login_required
def submit_review(doc_id):
    """Lưu đánh giá của user vào database."""
    doc = Document.query.get_or_404(doc_id)

    if doc.status != 'APPROVED':
        abort(403)

    # Không cho chủ tài liệu tự đánh giá
    if current_user.id == doc.uploader_id:
        flash('Bạn không thể đánh giá tài liệu của chính mình.', 'warning')
        return redirect(url_for('documents.detail', doc_id=doc_id))

    # Thay vì truy vấn CommunityReview, bây giờ ta dùng Ratings
    existing = Rating.query.filter_by(
        doc_id=doc_id,
        user_id=current_user.id
    ).first()
    if existing:
        flash('Bạn đã đánh giá tài liệu này rồi.', 'warning')
        return redirect(url_for('documents.detail', doc_id=doc_id))

    # Lấy dữ liệu từ form
    try:
        rating_value = int(request.form.get('rating', 0))
    except (ValueError, TypeError):
        rating_value = 0

    if rating_value < 1 or rating_value > 5:
        flash('Vui lòng chọn số sao từ 1 đến 5.', 'danger')
        return redirect(url_for('documents.detail', doc_id=doc_id))

    comment_text = request.form.get('comment', '').strip() or None

    try:
        new_rating = Rating(
            doc_id=doc_id,
            user_id=current_user.id,
            star_value=rating_value
        )
        db.session.add(new_rating)
        
        if comment_text:
            new_comment = Comment(
                document_id=doc_id,
                user_id=current_user.id,
                content=comment_text
            )
            db.session.add(new_comment)
            
        db.session.commit()
        flash('Cảm ơn bạn đã đánh giá! ⭐', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi khi gửi đánh giá: {str(e)}', 'danger')

    return redirect(url_for('documents.detail', doc_id=doc_id))


# ============================================================
# Route: GET /documents/<doc_id>/download - Tải xuống
# Khách vãng lai được phép tải xuống tài liệu đã duyệt
# ============================================================
@doc_bp.route('/documents/<string:doc_id>/download')
def download(doc_id):
    """
    Xử lý tải xuống file tài liệu:
    1. Yêu cầu đăng nhập - khách vãng lai không được tải
    2. Kiểm tra tài liệu tồn tại và đã được duyệt
    3. Tăng biến đếm downloads_count lên 1
    4. Gửi file về cho client
    """
    # Kiểm tra đăng nhập trước khi cho tải
    if not current_user.is_authenticated:
        flash('Vui lòng đăng nhập để tải tài liệu.', 'warning')
        return redirect(url_for('auth.login', next=request.url))
    doc = Document.query.get_or_404(doc_id)

    # Chỉ cho tải tài liệu đã được duyệt
    if doc.status != 'APPROVED':
        abort(403)

    # Tăng số lượt tải
    doc.download_count += 1
    
    # Ghi lại lịch sử tải
    download_history = DownloadHistory(user_id=current_user.id, document_id=doc_id)
    db.session.add(download_history)
    
    db.session.commit()

    # Xác định đường dẫn file thực tế
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_dir = os.path.join(upload_folder, os.path.dirname(doc.file_url))
    filename = os.path.basename(doc.file_url)

    # Kiểm tra file thực sự tồn tại trên disk
    if not os.path.exists(os.path.join(file_dir, filename)):
        flash('File không tồn tại trên server.', 'danger')
        return redirect(url_for('documents.detail', doc_id=doc_id))

    # as_attachment=True → browser sẽ hiện hộp thoại "Save As"
    return send_from_directory(file_dir, filename, as_attachment=True,
                               download_name=f"{doc.title}.{doc.file_format.lower()}")

# ============================================================
# Route: POST /documents/<doc_id>/review/edit - Sửa đánh giá
# ============================================================
@doc_bp.route('/documents/<string:doc_id>/review/edit', methods=['POST'])
@login_required
def edit_review(doc_id):
    """Cập nhật đánh giá của user."""
    doc = Document.query.get_or_404(doc_id)
    if doc.status != 'APPROVED': abort(403)
    
    existing_rating = Rating.query.filter_by(doc_id=doc_id, user_id=current_user.id).first()
    if not existing_rating:
        flash('Bạn chưa đánh giá tài liệu này.', 'warning')
        return redirect(url_for('documents.detail', doc_id=doc_id))
        
    try:
        rating_value = int(request.form.get('rating', existing_rating.star_value))
    except (ValueError, TypeError):
        rating_value = existing_rating.star_value
        
    if rating_value < 1 or rating_value > 5:
        flash('Vui lòng chọn số sao từ 1 đến 5.', 'danger')
        return redirect(url_for('documents.detail', doc_id=doc_id))
        
    comment_text = request.form.get('comment', '').strip() or None
    
    try:
        existing_rating.star_value = rating_value
        
        # Cập nhật hoặc thêm/xóa bình luận
        existing_comment = Comment.query.filter_by(document_id=doc_id, user_id=current_user.id).first()
        if existing_comment:
            if comment_text:
                existing_comment.content = comment_text
            else:
                db.session.delete(existing_comment)
        elif comment_text:
            new_comment = Comment(document_id=doc_id, user_id=current_user.id, content=comment_text)
            db.session.add(new_comment)
            
        db.session.commit()
        flash('Đã cập nhật đánh giá thành công! ⭐', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi cập nhật đánh giá: {str(e)}', 'danger')
        
    return redirect(url_for('documents.detail', doc_id=doc_id))

# ============================================================
# Route: POST /documents/<doc_id>/review/delete - Xóa đánh giá
# ============================================================
@doc_bp.route('/documents/<string:doc_id>/review/delete', methods=['POST'])
@login_required
def delete_review(doc_id):
    """Xóa bỏ đánh giá của user."""
    existing_rating = Rating.query.filter_by(doc_id=doc_id, user_id=current_user.id).first()
    if existing_rating:
        db.session.delete(existing_rating)
        
    existing_comment = Comment.query.filter_by(document_id=doc_id, user_id=current_user.id).first()
    if existing_comment:
        db.session.delete(existing_comment)
        
    db.session.commit()
    flash('Đã xóa đánh giá của bạn khỏi tài liệu.', 'info')
    return redirect(url_for('documents.detail', doc_id=doc_id))
