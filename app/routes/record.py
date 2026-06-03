import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import date, datetime, timedelta
from app.services.points import calculate_record_points

record_bp = Blueprint('record', __name__, url_prefix='/record')

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_user_streak_before(user_id, target_date_str):
    """計算使用者在指定日期之前的連續排便天數。"""
    conn = get_db_connection()
    records = conn.execute(
        'SELECT record_date FROM records WHERE user_id = ? ORDER BY record_date DESC', 
        (user_id,)
    ).fetchall()
    conn.close()
    
    recorded_dates = {r['record_date'] for r in records}
    
    # 解析目標日期，並取得其前一天
    target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
    check_date = target_date - timedelta(days=1)
    
    streak = 0
    # 從前一天往前遞減，檢查是否每天都有紀錄
    while check_date.strftime('%Y-%m-%d') in recorded_dates:
        streak += 1
        check_date -= timedelta(days=1)
        
    return streak

def update_team_points(team_id):
    """更新指定戰隊的總積分。"""
    conn = get_db_connection()
    try:
        # 計算該戰隊下所有使用者的總積分和
        result = conn.execute(
            '''
            SELECT SUM(r.points) as total 
            FROM records r 
            JOIN users u ON r.user_id = u.id 
            WHERE u.team_id = ?
            ''',
            (team_id,)
        ).fetchone()
        
        total_points = result['total'] if result['total'] is not None else 0.0
        
        # 更新 teams 表
        conn.execute(
            'UPDATE teams SET total_points = ? WHERE id = ?',
            (total_points, team_id)
        )
        conn.commit()
    except Exception as e:
        print(f"更新戰隊分數失敗: {e}")
    finally:
        conn.close()

@record_bp.route('/new', methods=['GET', 'POST'])
def new_record():
    user_id = session.get('user_id')
    team_id = session.get('team_id')
    if not user_id:
        flash('請先登入！', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        bristol_type = request.form.get('bristol_type')
        color = request.form.get('color')
        notes = request.form.get('notes', '').strip()
        record_date_str = request.form.get('record_date')

        # 預設為今天
        if not record_date_str:
            record_date_str = date.today().strftime('%Y-%m-%d')

        if not bristol_type or not color:
            flash('請選取便便形狀（布里斯托類型）與顏色！', 'danger')
            return render_template('new_record.html', today_str=date.today().strftime('%Y-%m-%d'))

        bristol_type = int(bristol_type)
        
        # 限制未來時間的輸入 (防呆機制)
        if record_date_str > date.today().strftime('%Y-%m-%d'):
            flash('不能記錄未來的日期！', 'danger')
            return render_template('new_record.html', today_str=date.today().strftime('%Y-%m-%d'))

        conn = get_db_connection()
        # 檢查該日期是否已經紀錄過
        existing = conn.execute(
            'SELECT id FROM records WHERE user_id = ? AND record_date = ?',
            (user_id, record_date_str)
        ).fetchone()

        if existing:
            flash(f'{record_date_str} 已經有排便紀錄囉！一天只能紀錄一次。', 'warning')
            conn.close()
            return redirect(url_for('dashboard.index'))

        # 計算本次紀錄的連續天數加成 (包含今天，所以是之前天數 + 1)
        streak_before = get_user_streak_before(user_id, record_date_str)
        streak_days = streak_before + 1

        # 呼叫積分服務計算積分
        points = calculate_record_points(bristol_type, color, streak_days)

        try:
            conn.execute(
                '''
                INSERT INTO records (user_id, record_date, bristol_type, color, points, notes) 
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (user_id, record_date_str, bristol_type, color, points, notes)
            )
            conn.commit()
            flash(f'記錄成功！本次排便獲得 {points} 積分！', 'success')
        except Exception as e:
            flash(f'新增紀錄失敗: {e}', 'danger')
        finally:
            conn.close()

        # 更新戰隊總分
        if team_id:
            update_team_points(team_id)

        return redirect(url_for('dashboard.index'))

    return render_template('new_record.html', today_str=date.today().strftime('%Y-%m-%d'))

@record_bp.route('/delete/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    user_id = session.get('user_id')
    team_id = session.get('team_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    # 確保是該使用者的紀錄才可以刪除
    record = conn.execute('SELECT * FROM records WHERE id = ? AND user_id = ?', (record_id, user_id)).fetchone()
    
    if not record:
        flash('找不到該紀錄或無權限刪除！', 'danger')
        conn.close()
        return redirect(url_for('dashboard.index'))

    try:
        conn.execute('DELETE FROM records WHERE id = ?', (record_id,))
        conn.commit()
        flash('紀錄已成功刪除。', 'success')
    except Exception as e:
        flash(f'刪除失敗: {e}', 'danger')
    finally:
        conn.close()

    # 重新計算並更新該戰隊的總積分
    if team_id:
        update_team_points(team_id)

    return redirect(url_for('dashboard.index'))
