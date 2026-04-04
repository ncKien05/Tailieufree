-- ============================================================
-- schema.sql - Cấu trúc cơ sở dữ liệu cho TailLieuFree
-- Tự động chạy khi MySQL container khởi động lần đầu
-- ============================================================

-- SỬA: Khai báo charset utf8mb4 để lưu tiếng Việt đúng cách
SET NAMES 'utf8mb4';
SET CHARACTER SET utf8mb4;

-- Bảng người dùng
-- SỬA: Thêm cột 'bio' (giới thiệu bản thân) và 'is_banned' (khóa tài khoản)
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,                          -- UUID dùng làm khóa chính
    email VARCHAR(255) UNIQUE NOT NULL,                  -- Email dùng để đăng nhập
    password_hash VARCHAR(255) NOT NULL,                 -- Mật khẩu đã được băm (bcrypt)
    full_name VARCHAR(100),                              -- Tên hiển thị
    avatar_url VARCHAR(255),                             -- Đường dẫn ảnh đại diện
    bio TEXT,                                            -- THÊM MỚI: Giới thiệu bản thân
    school VARCHAR(150),                                 -- Trường học
    major VARCHAR(150),                                  -- Ngành học
    role ENUM('USER', 'MOD', 'ADMIN') DEFAULT 'USER',   -- Phân quyền: thường/moderator/admin
    is_banned BOOLEAN DEFAULT FALSE,                     -- THÊM MỚI: TRUE = tài khoản bị khóa
    reputation_points INT DEFAULT 0,                     -- Điểm uy tín của người dùng
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP        -- Ngày tạo tài khoản
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng danh mục (môn học / chuyên mục)
-- SỬA: Thêm CHARSET=utf8mb4 để tên danh mục tiếng Việt hiển thị đúng
CREATE TABLE IF NOT EXISTS category (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,                          -- Tên danh mục (vd: Toán Cao Cấp)
    type ENUM('DOCUMENT', 'SUBJECT') NOT NULL            -- Loại: tài liệu hay môn học
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng tài liệu
-- SỬA: Thêm CHARSET=utf8mb4 để foreign key tương thích với bảng users
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(36) PRIMARY KEY,                          -- UUID dùng làm khóa chính
    uploader_id VARCHAR(36),                             -- Người upload (FK → users)
    title VARCHAR(255) NOT NULL,                         -- Tên tài liệu
    description TEXT,                                    -- Mô tả tài liệu
    file_url VARCHAR(255) NOT NULL,                      -- Đường dẫn file trên server
    file_format VARCHAR(10),                             -- Định dạng: PDF, DOCX, PPTX
    school_tag VARCHAR(150),                             -- Tag trường học liên quan
    academic_year VARCHAR(20),                           -- Năm học (vd: 2023-2024)
    category_id INT,                                     -- Danh mục (FK → category)
    status ENUM('PENDING', 'APPROVED', 'REJECTED') DEFAULT 'PENDING', -- Trạng thái kiểm duyệt
    downloads_count INT DEFAULT 0,                       -- Số lượt tải xuống
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,       -- Ngày upload
    FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE SET NULL
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Index để tăng tốc tìm kiếm
-- SỬA: Bỏ IF NOT EXISTS vì MySQL 8.0 không hỗ trợ cú pháp này cho CREATE INDEX
CREATE INDEX idx_document_title ON documents(title);
CREATE INDEX idx_document_school_tag ON documents(school_tag);
CREATE INDEX idx_document_status ON documents(status);

-- Bảng đánh giá cộng đồng (rating + comment)
-- SỬA: Thêm CHARSET=utf8mb4 để comment tiếng Việt hiển thị đúng
CREATE TABLE IF NOT EXISTS community_review (
    id INT PRIMARY KEY AUTO_INCREMENT,
    document_id VARCHAR(36),                             -- Tài liệu được đánh giá (FK → documents)
    user_id VARCHAR(36),                                 -- Người đánh giá (FK → users)
    rating SMALLINT NOT NULL CHECK (rating >= 1 AND rating <= 5), -- Điểm 1-5 sao
    comment TEXT,                                        -- Nội dung nhận xét
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
