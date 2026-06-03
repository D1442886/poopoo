from flask import Blueprint, render_template, session, redirect, url_for
import sqlite3

history_bp = Blueprint('history', __name__, template_folder='template4')

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@history_bp.route('/history')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login')) # 未登入先踢去登入

    conn = get_db_connection()
    # F-03 核心：依時間倒序撈出所有紀錄
    query = '''
        SELECT id, record_date, record_time, bristol_type, poop_color, memo 
        FROM records 
        WHERE user_id = ? 
        ORDER BY record_date DESC, record_time DESC
    '''
    records = conn.execute(query, (user_id,)).fetchall()
    conn.close()

    return render_template('history.html', records=records)
