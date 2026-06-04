CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    total_points REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    team_id INTEGER,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(team_id) REFERENCES teams(id)
);

CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    record_date TEXT NOT NULL, -- YYYY-MM-DD
    bristol_type INTEGER NOT NULL, -- 1-7
    color TEXT NOT NULL, -- brown, yellow, green, black, red, pale
    points REAL DEFAULT 0.0,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
