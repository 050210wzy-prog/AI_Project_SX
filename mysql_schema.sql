CREATE DATABASE IF NOT EXISTS admission_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE admission_system;

CREATE TABLE IF NOT EXISTS users (
  id VARCHAR(36) PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  email VARCHAR(100),
  role VARCHAR(50) DEFAULT 'user',
  is_active TINYINT DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS roles (
  id INT PRIMARY KEY AUTO_INCREMENT,
  role_key VARCHAR(50) UNIQUE NOT NULL,
  role_name VARCHAR(100) NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS permissions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  perm_key VARCHAR(100) UNIQUE NOT NULL,
  perm_name VARCHAR(100) NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS role_permissions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  role_key VARCHAR(50) NOT NULL,
  perm_key VARCHAR(100) NOT NULL,
  UNIQUE KEY uk_role_perm (role_key, perm_key)
);

CREATE TABLE IF NOT EXISTS majors (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) UNIQUE NOT NULL,
  code VARCHAR(50),
  college VARCHAR(100),
  duration VARCHAR(20),
  tuition DECIMAL(10,2),
  degree VARCHAR(50),
  description TEXT,
  courses TEXT,
  jobs TEXT,
  features TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admission_plans (
  id INT PRIMARY KEY AUTO_INCREMENT,
  year INT NOT NULL,
  province VARCHAR(50),
  subject VARCHAR(50),
  major VARCHAR(100) NOT NULL,
  plan_count INT DEFAULT 0,
  batch_name VARCHAR(100),
  remark TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_plan (year, province, subject, major)
);

CREATE TABLE IF NOT EXISTS scores (
  id INT PRIMARY KEY AUTO_INCREMENT,
  year INT NOT NULL,
  major VARCHAR(100) NOT NULL,
  max_score DECIMAL(8,2),
  min_score DECIMAL(8,2) NOT NULL,
  avg_score DECIMAL(8,2),
  rank_min INT,
  control_line DECIMAL(8,2),
  enrollment INT,
  province VARCHAR(50),
  subject VARCHAR(50),
  source VARCHAR(255),
  INDEX idx_score (year, province, subject, major)
);

CREATE TABLE IF NOT EXISTS rank_segments (
  id INT PRIMARY KEY AUTO_INCREMENT,
  year INT NOT NULL,
  province VARCHAR(50),
  subject VARCHAR(50),
  score DECIMAL(8,2) NOT NULL,
  rank_count INT DEFAULT 0,
  cumulative_rank INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_rank_segment (year, province, subject, score)
);

CREATE TABLE IF NOT EXISTS documents (
  id VARCHAR(36) PRIMARY KEY,
  filename VARCHAR(255) NOT NULL,
  doc_type VARCHAR(20),
  chunks INT DEFAULT 0,
  status VARCHAR(50) DEFAULT 'completed',
  version_no INT DEFAULT 1,
  category VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_versions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  document_id VARCHAR(36),
  filename VARCHAR(255),
  version_no INT DEFAULT 1,
  chunk_count INT DEFAULT 0,
  status VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tickets (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL,
  category VARCHAR(50),
  question TEXT NOT NULL,
  contact VARCHAR(100),
  priority VARCHAR(50) DEFAULT '普通',
  assignee VARCHAR(100),
  status VARCHAR(50) DEFAULT '待处理',
  reply TEXT,
  satisfaction INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ticket_replies (
  id INT PRIMARY KEY AUTO_INCREMENT,
  ticket_id INT NOT NULL,
  replier VARCHAR(100),
  reply TEXT NOT NULL,
  internal_note TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS students (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_no VARCHAR(50) UNIQUE,
  name VARCHAR(50) NOT NULL,
  gender VARCHAR(20),
  id_card VARCHAR(30),
  phone VARCHAR(30),
  email VARCHAR(100),
  province VARCHAR(50),
  subject VARCHAR(50),
  score DECIMAL(8,2),
  intended_major VARCHAR(100),
  admitted_major VARCHAR(100),
  admission_status VARCHAR(50),
  college VARCHAR(100),
  class_name VARCHAR(100),
  enrollment_year INT
);

CREATE TABLE IF NOT EXISTS conversations (
  id VARCHAR(36) PRIMARY KEY,
  session_id VARCHAR(100),
  question TEXT,
  answer TEXT,
  intent VARCHAR(50),
  sources JSON,
  confidence DECIMAL(5,2),
  response_time INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS operation_logs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id VARCHAR(36),
  operation_type VARCHAR(50),
  target_id VARCHAR(100),
  details JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_operation (operation_type, created_at)
);

CREATE TABLE IF NOT EXISTS site_channels (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  parent VARCHAR(100),
  slug VARCHAR(100) UNIQUE,
  channel_type VARCHAR(50) DEFAULT 'list',
  sort_order INT DEFAULT 0,
  is_nav TINYINT DEFAULT 1,
  is_active TINYINT DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS site_articles (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL,
  channel VARCHAR(100),
  summary TEXT,
  content LONGTEXT,
  source VARCHAR(100),
  author VARCHAR(100),
  cover_url VARCHAR(500),
  publish_status VARCHAR(50) DEFAULT '已发布',
  review_status VARCHAR(50) DEFAULT '已发布',
  review_comment TEXT,
  reviewer VARCHAR(100),
  reviewed_at DATETIME,
  is_top TINYINT DEFAULT 0,
  view_count INT DEFAULT 0,
  publish_date DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_site_article (channel, publish_status, publish_date),
  INDEX idx_site_review (review_status, reviewed_at)
);

CREATE TABLE IF NOT EXISTS site_banners (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL,
  subtitle TEXT,
  image_url VARCHAR(500),
  link_url VARCHAR(500),
  sort_order INT DEFAULT 0,
  is_active TINYINT DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS site_links (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(100) NOT NULL,
  url VARCHAR(500),
  link_type VARCHAR(50) DEFAULT '快捷入口',
  sort_order INT DEFAULT 0,
  is_active TINYINT DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS site_settings (
  id INT PRIMARY KEY AUTO_INCREMENT,
  setting_key VARCHAR(100) UNIQUE NOT NULL,
  setting_value TEXT,
  description TEXT,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS site_attachments (
  id INT PRIMARY KEY AUTO_INCREMENT,
  article_id INT,
  file_name VARCHAR(255) NOT NULL,
  file_url VARCHAR(500),
  file_type VARCHAR(50),
  file_size INT DEFAULT 0,
  download_count INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_site_attachment_article (article_id)
);

CREATE TABLE IF NOT EXISTS site_audit_logs (
  id INT PRIMARY KEY AUTO_INCREMENT,
  article_id INT,
  action VARCHAR(50) NOT NULL,
  operator VARCHAR(100),
  comment TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_site_audit_article (article_id),
  INDEX idx_site_audit_created (created_at)
);

CREATE TABLE IF NOT EXISTS site_college_profiles (
  id INT PRIMARY KEY AUTO_INCREMENT,
  college_name VARCHAR(100) UNIQUE NOT NULL,
  summary TEXT,
  majors TEXT,
  contact VARCHAR(255),
  sort_order INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS site_major_profiles (
  id INT PRIMARY KEY AUTO_INCREMENT,
  major_name VARCHAR(100) UNIQUE NOT NULL,
  college_name VARCHAR(100),
  duration VARCHAR(50),
  tuition VARCHAR(100),
  core_courses TEXT,
  jobs TEXT,
  feature_text TEXT,
  sort_order INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_site_major_college (college_name)
);
