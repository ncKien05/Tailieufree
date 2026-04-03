CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY, 
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url VARCHAR(255),
    school VARCHAR(150),
    major VARCHAR(150),
    role VARCHAR(20) DEFAULT 'USER' CHECK (role IN ('USER', 'MOD', 'ADMIN')),
    reputation_points INTEGER DEFAULT 0
);

CREATE TABLE category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('DOCUMENT', 'SUBJECT'))
);
CREATE TABLE documents (
    id VARCHAR(36) PRIMARY KEY,
    uploader_id VARCHAR(36),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_url VARCHAR(255) NOT NULL,
    file_format VARCHAR(10),
    school_tag VARCHAR(150),
    academic_year VARCHAR(20),
    category_id INTEGER,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
    downloads_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE SET NULL
);

CREATE INDEX idx_document_title ON documents(title);
CREATE INDEX idx_document_school_tag ON documents(school_tag);

CREATE TABLE community_review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id VARCHAR(36),
    user_id VARCHAR(36),
    rating SMALLINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
