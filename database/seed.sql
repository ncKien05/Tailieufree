-- ============================================================
-- seed.sql - Dữ liệu mẫu ban đầu cho TailLieuFree
-- Tự động chạy sau schema.sql khi MySQL container khởi động
-- ============================================================

-- SỬA: Khai báo charset utf8mb4 để tiếng Việt hiển thị đúng
SET NAMES 'utf8mb4';
SET CHARACTER SET utf8mb4;

-- -------------------------------------------------------
-- LƯU Ý VỀ TÀI KHOẢN ADMIN:
-- Admin KHÔNG được tạo ở đây vì mật khẩu cần được mã hóa
-- bằng thư viện bcrypt - không thể làm trong SQL thuần túy.
-- Sau khi container chạy, tạo admin bằng lệnh:
--   docker-compose exec web flask create-admin
-- -------------------------------------------------------

-- -------------------------------------------------------
-- Danh mục môn học mặc định (type = SUBJECT)
-- SỬA: Thêm CHARACTER SET để tiếng Việt không bị lỗi font
-- -------------------------------------------------------
INSERT IGNORE INTO category (name, type) VALUES
    ('Toán Cao Cấp',            'SUBJECT'),
    ('Vật Lý Đại Cương',        'SUBJECT'),
    ('Hóa Học Đại Cương',       'SUBJECT'),
    ('Lập Trình Cơ Bản',        'SUBJECT'),
    ('Cấu Trúc Dữ Liệu',        'SUBJECT'),
    ('Cơ Sở Dữ Liệu',           'SUBJECT'),
    ('Mạng Máy Tính',            'SUBJECT'),
    ('Kinh Tế Vi Mô',            'SUBJECT'),
    ('Kinh Tế Vĩ Mô',            'SUBJECT'),
    ('Tiếng Anh Chuyên Ngành',  'SUBJECT'),
    ('Triết Học Mác-Lênin',     'SUBJECT'),
    ('Tư Tưởng Hồ Chí Minh',    'SUBJECT');

-- -------------------------------------------------------
-- Danh mục loại tài liệu (type = DOCUMENT)
-- -------------------------------------------------------
INSERT IGNORE INTO category (name, type) VALUES
    ('Đề Thi + Đáp Án',         'DOCUMENT'),
    ('Giáo Trình',               'DOCUMENT'),
    ('Bài Tập + Lời Giải',      'DOCUMENT'),
    ('Tóm Tắt Lý Thuyết',       'DOCUMENT'),
    ('Luận Văn / Đồ Án',        'DOCUMENT'),
    ('Slide Bài Giảng',          'DOCUMENT');
