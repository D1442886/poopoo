from flask import Blueprint, render_template, session, redirect, url_for, jsonify
import sqlite3

analytics_bp = Blueprint('analytics', __name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@analytics_bp.route('/analytics')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    return render_template('analytics.html')

# API 路由：專門丟 JSON 資料給 Chart.js 畫圖
@analytics_bp.route('/api/analytics-data')
def analytics_data():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    # 統計該使用者各種布里斯托大便類型 (1~7型) 的數量
    # 假設欄位叫 bristol_type
    query = '''
        SELECT bristol_type, COUNT(*) as count 
        FROM records 
        WHERE user_id = ? 
        GROUP BY bristol_type
    '''
    rows = conn.execute(query, (user_id,)).fetchall()
    conn.close()

    # 初始化 1~7 型的數據預設為 0
    stats = {str(i): 0 for i in range(1, 8)}
    for row in rows:
        stats[str(row['bristol_type'])] = row['count']

    # 包裝成前端 Chart.js 好讀的格式
    chart_data = {
        'labels': ['第一型 (硬球狀)', '第二型 (香腸狀但表面凹凸)', '第三型 (香腸狀但表面有裂痕)', '第四型 (光滑蛇狀-完美)', '第五型 (柔軟塊狀)', '第六型 (糊狀)', '第七型 (水狀)'],
        'data': [stats['1'], stats['2'], stats['3'], stats['4'], stats['5'], stats['6'], stats['7']]
    }
    
    return jsonify(chart_data)