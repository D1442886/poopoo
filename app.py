import os
import sqlite3
from flask import Flask, redirect, url_for

def init_db():
    """初始化資料庫，建立資料表並預填戰隊資料。"""
    db_path = 'database.db'
    schema_path = os.path.join('database', 'schema.sql')
    
    # 確保 database 目錄存在 (雖然通常 schema.sql 已存在)
    os.makedirs('database', exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    try:
        # 1. 執行 schema.sql 建立資料表
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
        
        # 2. 檢查並預填戰隊資料
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM teams")
        count = cursor.fetchone()[0]
        
        if count == 0:
            default_teams = [
                ('高纖香蕉戰隊', '追求最完美的類型 4 香蕉便便，以高纖飲食為核心！'),
                ('狂暴多水戰隊', '水分能解決一切宿便，狂灌水就是我們的信仰！'),
                ('益生菌先鋒隊', '依靠強大的腸道好菌，天天優格與益生菌拉出新高度！'),
                ('乳酸菌衝鋒隊', '每日發酵乳製品愛好者，養樂多與優酪乳是我們的靈魂！')
            ]
            cursor.executemany(
                "INSERT INTO teams (name, description, total_points) VALUES (?, ?, 0.0)",
                default_teams
            )
            conn.commit()
            print("已成功預填 4 個預設戰隊！")
    except Exception as e:
        print(f"資料庫初始化失敗: {e}")
    finally:
        conn.close()

def create_app():
    """建立並設定 Flask 應用程式。"""
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    app.config['SECRET_KEY'] = 'poopoo-championship-secret-key-12345'
    
    # 初始化資料庫
    init_db()
    
    # 註冊 Blueprints
    from app.routes.dashboard import dashboard_bp
    from app.routes.auth import auth_bp
    from app.routes.record import record_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(record_bp)
    
    @app.route('/')
    def root():
        return redirect(url_for('dashboard.index'))
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
