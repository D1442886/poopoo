-- SQLite Database Schema for Poop Champion Tournament System

PRAGMA foreign_keys = ON;

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    equipped_title TEXT DEFAULT '拉屎新手',
    score INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. RECORDS TABLE
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bristol_type INTEGER NOT NULL CHECK (bristol_type BETWEEN 1 AND 7),
    color TEXT NOT NULL,
    duration INTEGER, -- stored in seconds
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. TOURNAMENTS TABLE
CREATE TABLE IF NOT EXISTS tournaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. TOURNAMENT_MEMBERS TABLE
CREATE TABLE IF NOT EXISTS tournament_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(tournament_id, user_id)
);

-- 5. ACHIEVEMENTS TABLE
CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    condition_type TEXT NOT NULL,
    condition_value INTEGER NOT NULL
);

-- 6. USER_ACHIEVEMENTS TABLE
CREATE TABLE IF NOT EXISTS user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE,
    UNIQUE(user_id, achievement_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_records_user ON records(user_id);
CREATE INDEX IF NOT EXISTS idx_tournament_members_user ON tournament_members(user_id);
CREATE INDEX IF NOT EXISTS idx_tournament_members_room ON tournament_members(tournament_id);
CREATE INDEX IF NOT EXISTS idx_user_achievements_user ON user_achievements(user_id);

-- Seeding Default Achievements
INSERT OR IGNORE INTO achievements (name, description, condition_type, condition_value) VALUES 
('初試身手', '完成第一次排便紀錄', 'total_count', 1),
('馬桶之王', '累計完成 10 次排便紀錄', 'total_count', 10),
('煉金術士', '累計記錄 5 次健康的「第 4 型（黃金香蕉）」大便', 'bristol_healthy_count', 5),
('速戰速決', '在 2 分鐘（120秒）內完成一次排便紀錄', 'duration_under', 120),
('定時炸彈', '連續 3 次在同一時段（例如早上 8:00 - 9:00）完成排便紀錄', 'regularity_count', 3);
