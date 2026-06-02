from flask import Blueprint, render_template, session, redirect, url_for
from datetime import date, timedelta
import sqlite3

dashboard_bp = Blueprint('dashboard', __name__)

def get_db_connection():
    # 這裡連結你們前期定案的 SQLite 資料庫 [cite: 47, 55]
    conn = sqlite3.connect('database.db') 
    conn.row_factory = sqlite3.Row
    return conn

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
def index():
    # 串接 F-01 會員系統的 session [cite: 43, 58]
    user_id = session.get('user_id')
    user_name = session.get('user_name', '神祕選手')
    
    if not user_id:
        return redirect(url_for('auth.login')) # 未登入先導向登入頁

    conn = get_db_connection()
    # 撈取使用者的排便紀錄
    records = conn.execute(
        'SELECT record_date FROM records WHERE user_id = ? ORDER BY record_date DESC', 
        (user_id,)
    ).fetchall()
    conn.close()

    today_str = date.today().strftime('%Y-%m-%d')
    yesterday_str = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    recorded_dates = [r['record_date'] for r in records]

    # F-02 核心功能：今日是否已紀錄 [cite: 43]
    today_recorded = today_str in recorded_dates

    # F-02 核心功能：連續天數計算 [cite: 43]
    streak_days = 0
    if today_str in recorded_dates or yesterday_str in recorded_dates:
        check_date = date.today() if today_str in recorded_dates else date.today() - timedelta(days=1)
        while check_date.strftime('%Y-%m-%d') in recorded_dates:
            streak_days += 1
            check_date -= timedelta(days=1)
    else:
        streak_days = 0

    return render_template(
        'dashboard.html',
        user_name=user_name,
        today_recorded=today_recorded,
        streak_days=streak_days
    )