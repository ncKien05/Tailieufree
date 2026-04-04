# ============================================================
# app/forms.py - Tất cả các Form sử dụng Flask-WTF
# Flask-WTF cung cấp: CSRF protection, validation tự động
# ============================================================

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, TextAreaField,
                     SelectField, SubmitField, BooleanField)
from wtforms.validators import (DataRequired, Email, Length,
                                EqualTo, Optional, ValidationError)
from .models import User


# ============================================================
# Form: Đăng ký tài khoản mới
# ============================================================
class RegisterForm(FlaskForm):
    full_name = StringField('Họ và tên',
                            validators=[DataRequired(message='Vui lòng nhập họ tên'),
                                        Length(min=2, max=100)])
    email = StringField('Email',
                        validators=[DataRequired(), Email(message='Email không hợp lệ')])
    password = PasswordField('Mật khẩu',
                             validators=[DataRequired(),
                                         Length(min=6, message='Mật khẩu ít nhất 6 ký tự')])
    confirm_password = PasswordField('Xác nhận mật khẩu',
                                     validators=[DataRequired(),
                                                 EqualTo('password', message='Mật khẩu không khớp')])
    submit = SubmitField('Đăng Ký')

    # Custom validator: kiểm tra email đã tồn tại chưa
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email này đã được sử dụng.')


# ============================================================
# Form: Đăng nhập
# ============================================================
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu',
                             validators=[DataRequired()])
    remember = BooleanField('Ghi nhớ đăng nhập')
    submit = SubmitField('Đăng Nhập')


# ============================================================
# Form: Upload tài liệu
# ============================================================
class UploadDocForm(FlaskForm):
    title = StringField('Tên tài liệu',
                        validators=[DataRequired(message='Tên tài liệu không được để trống'),
                                    Length(max=255)])
    description = TextAreaField('Mô tả',
                                validators=[Optional(), Length(max=2000)])
    school_tag = StringField('Trường (tag)',
                             validators=[Optional(), Length(max=150)])
    academic_year = StringField('Năm học (vd: 2023-2024)',
                                validators=[Optional(), Length(max=20)])
    # Danh mục sẽ được populate động từ database trong route
    category_id = SelectField('Danh mục / Môn học', coerce=int,
                              validators=[Optional()])
    # Chỉ cho phép upload PDF, DOCX, PPTX
    document_file = FileField('Chọn file tài liệu',
                              validators=[
                                  DataRequired(message='Vui lòng chọn file'),
                                  FileAllowed(['pdf', 'docx', 'pptx'],
                                              'Chỉ chấp nhận PDF, DOCX, PPTX!')
                              ])
    submit = SubmitField('Tải Lên')


# ============================================================
# Form: Chỉnh sửa thông tin hồ sơ cá nhân
# ============================================================
class EditProfileForm(FlaskForm):
    full_name = StringField('Họ và tên',
                            validators=[DataRequired(), Length(min=2, max=100)])
    school = StringField('Trường học',
                         validators=[Optional(), Length(max=150)])
    major = StringField('Ngành học',
                        validators=[Optional(), Length(max=150)])
    bio = TextAreaField('Giới thiệu bản thân',
                        validators=[Optional(), Length(max=1000)])
    # Cho phép upload ảnh đại diện (tùy chọn)
    avatar = FileField('Ảnh đại diện (tùy chọn)',
                       validators=[Optional(),
                                   FileAllowed(['jpg', 'jpeg', 'png', 'gif'],
                                               'Chỉ chấp nhận ảnh JPG, PNG, GIF!')])
    submit = SubmitField('Cập Nhật')


# ============================================================
# Form: Đổi mật khẩu
# ============================================================
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Mật khẩu hiện tại',
                                     validators=[DataRequired()])
    new_password = PasswordField('Mật khẩu mới',
                                 validators=[DataRequired(),
                                             Length(min=6, message='Ít nhất 6 ký tự')])
    confirm_new_password = PasswordField('Xác nhận mật khẩu mới',
                                         validators=[DataRequired(),
                                                     EqualTo('new_password',
                                                             message='Mật khẩu mới không khớp')])
    submit = SubmitField('Đổi Mật Khẩu')


# ============================================================
# Form: Chỉnh sửa tên tài liệu (dành cho chủ tài liệu)
# ============================================================
class EditDocTitleForm(FlaskForm):
    title = StringField('Tên tài liệu mới',
                        validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Mô tả',
                                validators=[Optional(), Length(max=2000)])
    submit = SubmitField('Lưu Thay Đổi')


# ============================================================
# Form: Quản lý danh mục (Admin)
# ============================================================
class CategoryForm(FlaskForm):
    name = StringField('Tên danh mục',
                       validators=[DataRequired(), Length(max=100)])
    type = SelectField('Loại',
                       choices=[('SUBJECT', 'Môn học'), ('DOCUMENT', 'Loại tài liệu')],
                       validators=[DataRequired()])
    submit = SubmitField('Lưu')
