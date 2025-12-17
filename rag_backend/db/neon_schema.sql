-- Neon Postgres Schema for Physical AI & Humanoid Robotics Book

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    software_background JSONB,
    hardware_background JSONB,
    preferences JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ingestion log table
CREATE TABLE IF NOT EXISTS ingest_log (
    doc_id VARCHAR(255) PRIMARY KEY,
    path TEXT NOT NULL,
    version VARCHAR(50),
    last_indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    chunk_count INTEGER DEFAULT 0
);

-- Personalized documents cache table
CREATE TABLE IF NOT EXISTS personalized_docs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    doc_path VARCHAR(500) NOT NULL,
    mode VARCHAR(50) NOT NULL,  -- 'simpler', 'advanced', 'visual', 'code-heavy'
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 day'),
    UNIQUE(user_id, doc_path, mode)
);

-- Translations cache table
CREATE TABLE IF NOT EXISTS translations (
    id SERIAL PRIMARY KEY,
    doc_path VARCHAR(500) NOT NULL,
    target_language VARCHAR(10) NOT NULL,  -- 'ur', 'en', etc.
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doc_path, target_language)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_last_active ON sessions(last_active);
CREATE INDEX IF NOT EXISTS idx_personalized_docs_user_doc_mode ON personalized_docs(user_id, doc_path, mode);
CREATE INDEX IF NOT EXISTS idx_translations_doc_lang ON translations(doc_path, target_language);