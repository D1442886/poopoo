import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    conn = get_db_connection()
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        team_id = request.form.get('team_id')

        if not username or not password or not team_id:
            flash('所有欄位皆為必填！', 'danger')
            teams = conn.execute('SELECT * FROM teams').fetchall()
            conn.close()
            return render_template('register.html', teams=teams)

        try:
            password_hash = generate_password_hash(password)
            conn.execute(
                'INSERT INTO users (username, password_hash, team_id) VALUES (?, ?, ?)',
                (username, password_hash, int(team_id))
            )
            conn.commit()
            flash('註冊成功，請登入！', 'success')
            conn.close()
            return redirect(url_for('auth.login'))
        except sqlite3.IntegrityError:
            flash('該帳號名稱已被註冊，請換一個！', 'danger')
        except Exception as e:
            flash(f'發生錯誤: {e}', 'danger')

    teams = conn.execute('SELECT * FROM teams').fetchall()
    conn.close()
    return render_template('register.html', teams=teams)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('請輸入帳號與密碼！', 'danger')
            return render_template('login.html')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['username']
            session['team_id'] = user['team_id']
            flash(f'歡迎回來，{user["username"]}！', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('帳號或密碼錯誤！', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('您已成功登出。', 'info')
    return redirect(url_for('auth.login'))
