import sqlite3
import os

DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'instance',
    'database.db'
)

SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'database',
    'schema.sql'
)

def get_db_connection():
    """建立資料庫連線，並設定 row_factory 以便透過欄位名稱存取"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """初始化資料庫：讀取 schema.sql 並執行建表"""
    conn = get_db_connection()
    try:
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()
