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
    ('Tư Tưởng Hồ Chí Minh',    'SUBJECT'),
    ('Python',                  'SUBJECT'),
    ('Giải Tích 1',             'SUBJECT'),
    ('Giải Tích 2',             'SUBJECT'),
    ('Giải Tích 3',             'SUBJECT'),
    ('Xác Suất Thống Kê',       'SUBJECT'),
    ('Đại Số Tuyến Tính',       'SUBJECT'),
    ('Vật Lý Đại Cương 1',      'SUBJECT');

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

-- -------------------------------------------------------
-- Thêm các tài khoản người đăng (giảng viên) mẫu
-- -------------------------------------------------------
INSERT IGNORE INTO users (id, email, password_hash, full_name, role, is_banned) VALUES
    ('teacher-1', 'nguyenduy@example.com', 'dummy', 'Thầy Nguyễn Duy', 'USER', FALSE),
    ('teacher-2', 'nguyenhai@example.com', 'dummy', 'Thầy Nguyễn Hải', 'USER', FALSE),
    ('teacher-3', 'thuyduong@example.com', 'dummy', 'Cô Thùy Dương', 'USER', FALSE),
    ('teacher-4', 'son@example.com', 'dummy', 'Thầy Sơn', 'USER', FALSE),
    ('teacher-5', 'nguyennam@example.com', 'dummy', 'Thầy Nguyễn Nam', 'USER', FALSE);

-- -------------------------------------------------------
-- Thêm các tài liệu mẫu theo yêu cầu
-- -------------------------------------------------------
INSERT IGNORE INTO documents (id, uploader_id, title, description, file_url, file_format, category_id, status) VALUES
    ('doc-1', 'teacher-1', 'Tài liệu giải tích 1', 'Tài liệu môn Giải Tích 1', 'documents/sample_document.pdf', 'PDF', (SELECT id FROM category WHERE name = 'Giải Tích 1' LIMIT 1), 'APPROVED'),
    ('doc-2', 'teacher-2', 'Tài Liệu Giải tích 2', 'Tài liệu môn Giải Tích 2', 'documents/sample_document.pdf', 'PDF', (SELECT id FROM category WHERE name = 'Giải Tích 2' LIMIT 1), 'APPROVED'),
    ('doc-3', 'teacher-2', 'Tài liệu Giải tích 3', 'Tài liệu môn Giải Tích 3', 'documents/sample_document.pdf', 'PDF', (SELECT id FROM category WHERE name = 'Giải Tích 3' LIMIT 1), 'APPROVED'),
    ('doc-4', 'teacher-3', 'Xác suất thống kê', 'Tài liệu môn Xác Suất Thống Kê', 'documents/sample_document.pdf', 'PDF', (SELECT id FROM category WHERE name = 'Xác Suất Thống Kê' LIMIT 1), 'APPROVED'),
    ('doc-5', 'teacher-4', 'Tài liệu đại số', 'Tài liệu môn Đại Số Tuyến Tính', 'documents/sample_document.pdf', 'PDF', (SELECT id FROM category WHERE name = 'Đại Số Tuyến Tính' LIMIT 1), 'APPROVED'),
    ('doc-6', 'teacher-5', 'Vật lí Đại cương 1', 'Tài liệu môn Vật Lý Đại Cương 1', 'documents/sample_document.pdf', 'PDF', (SELECT id FROM category WHERE name = 'Vật Lý Đại Cương 1' LIMIT 1), 'APPROVED');

