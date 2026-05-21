from app.models.db import get_db_connection

class User:
    def __init__(self, id, username, password_hash, equipped_title='拉屎新手', score=0, created_at=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.equipped_title = equipped_title
        self.score = score
        self.created_at = created_at

    @staticmethod
    def create(username, password_hash):
        """新增使用者"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_by_id(user_id):
        """依據 id 取得使用者"""
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                password_hash=row['password_hash'],
                equipped_title=row['equipped_title'],
                score=row['score'],
                created_at=row['created_at']
            )
        return None

    @staticmethod
    def get_by_username(username):
        """依據使用者名稱取得使用者"""
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                password_hash=row['password_hash'],
                equipped_title=row['equipped_title'],
                score=row['score'],
                created_at=row['created_at']
            )
        return None

    @staticmethod
    def get_all():
        """取得所有使用者（依積分排序）"""
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM users ORDER BY score DESC").fetchall()
        conn.close()
        return [
            User(
                id=row['id'],
                username=row['username'],
                password_hash=row['password_hash'],
                equipped_title=row['equipped_title'],
                score=row['score'],
                created_at=row['created_at']
            )
            for row in rows
        ]

    @staticmethod
    def update_profile(user_id, score=None, equipped_title=None):
        """更新使用者積分或稱號"""
        conn = get_db_connection()
        try:
            if score is not None:
                conn.execute("UPDATE users SET score = ? WHERE id = ?", (score, user_id))
            if equipped_title is not None:
                conn.execute("UPDATE users SET equipped_title = ? WHERE id = ?", (equipped_title, user_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def delete(user_id):
        """刪除使用者"""
        conn = get_db_connection()
        try:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
