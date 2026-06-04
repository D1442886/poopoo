from flask import Blueprint, render_template, session, redirect, url_for
from datetime import date, timedelta
import sqlite3

dashboard_bp = Blueprint('dashboard', __name__)

def get_db_connection():
    conn = sqlite3.connect('database.db') 
    conn.row_factory = sqlite3.Row
    return conn

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
def index():
    user_id = session.get('user_id')
    user_name = session.get('user_name', '神祕選手')
    
    if not user_id:
        return redirect(url_for('auth.login')) # 未登入先導向登入頁

    conn = get_db_connection()
    
    # 1. 撈取使用者的所有排便紀錄 (用來計算連續天數與顯示歷史清單)
    records = conn.execute(
        'SELECT * FROM records WHERE user_id = ? ORDER BY record_date DESC, id DESC', 
        (user_id,)
    ).fetchall()
    
    # 2. 撈取使用者的所屬戰隊資訊
    user_team = conn.execute(
        '''
        SELECT t.name, t.total_points, t.description 
        FROM teams t 
        JOIN users u ON u.team_id = t.id 
        WHERE u.id = ?
        ''',
        (user_id,)
    ).fetchone()

    # 3. 撈取所有戰隊的積分排行榜 (由高到低)
    team_leaderboard = conn.execute(
        'SELECT name, total_points, description FROM teams ORDER BY total_points DESC'
    ).fetchall()

    # 4. 撈取全服本週貢獻度最高的 MVP (歷史總分最高的使用者作為 MVP)
    mvp_user = conn.execute(
        '''
        SELECT u.username, SUM(r.points) as total_contrib, t.name as team_name
        FROM records r
        JOIN users u ON r.user_id = u.id
        JOIN teams t ON u.team_id = t.id
        GROUP BY u.id
        ORDER BY total_contrib DESC
        LIMIT 1
        '''
    ).fetchone()

    conn.close()

    today_str = date.today().strftime('%Y-%m-%d')
    yesterday_str = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    recorded_dates = [r['record_date'] for r in records]

    # F-02 核心功能：今日是否已紀錄
    today_recorded = today_str in recorded_dates

    # F-02 核心功能：連續天數計算 (考量今天或昨天是否有紀錄)
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
        user_team=user_team,
        today_recorded=today_recorded,
        streak_days=streak_days,
        records=records[:10], # 只顯示最近 10 筆紀錄
        team_leaderboard=team_leaderboard,
        mvp_user=mvp_user
    )