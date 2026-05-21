from app.models.db import get_db_connection

class Tournament:
    def __init__(self, id, name, code, created_by, created_at=None):
        self.id = id
        self.name = name
        self.code = code
        self.created_by = created_by
        self.created_at = created_at

    @staticmethod
    def create(name, code, created_by):
        """新增爭霸賽房間"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # 1. 建立房間
            cursor.execute(
                "INSERT INTO tournaments (name, code, created_by) VALUES (?, ?, ?)",
                (name, code, created_by)
            )
            tournament_id = cursor.lastrowid
            
            # 2. 自動將創建者加入房間成員
            cursor.execute(
                "INSERT INTO tournament_members (tournament_id, user_id) VALUES (?, ?)",
                (tournament_id, created_by)
            )
            conn.commit()
            return tournament_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_by_id(tournament_id):
        """取得房間資訊"""
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,)).fetchone()
        conn.close()
        if row:
            return Tournament(
                id=row['id'],
                name=row['name'],
                code=row['code'],
                created_by=row['created_by'],
                created_at=row['created_at']
            )
        return None

    @staticmethod
    def get_by_code(code):
        """依邀請碼取得房間"""
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM tournaments WHERE code = ?", (code,)).fetchone()
        conn.close()
        if row:
            return Tournament(
                id=row['id'],
                name=row['name'],
                code=row['code'],
                created_by=row['created_by'],
                created_at=row['created_at']
            )
        return None

    @staticmethod
    def add_member(tournament_id, user_id):
        """加入房間成員"""
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO tournament_members (tournament_id, user_id) VALUES (?, ?)",
                (tournament_id, user_id)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # 已經是成員了，不做任何事
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_members(tournament_id):
        """取得房間內所有成員及其積分（依積分高低排序）"""
        conn = get_db_connection()
        rows = conn.execute(
            """
            SELECT u.id, u.username, u.score, u.equipped_title, tm.joined_at
            FROM tournament_members tm
            JOIN users u ON tm.user_id = u.id
            WHERE tm.tournament_id = ?
            ORDER BY u.score DESC
            """,
            (tournament_id,)
        ).fetchall()
        conn.close()
        return [
            {
                "id": row["id"],
                "username": row["username"],
                "score": row["score"],
                "equipped_title": row["equipped_title"],
                "joined_at": row["joined_at"]
            }
            for row in rows
        ]

    @staticmethod
    def get_user_tournaments(user_id):
        """取得使用者加入的所有爭霸賽房間"""
        conn = get_db_connection()
        rows = conn.execute(
            """
            SELECT t.* 
            FROM tournament_members tm
            JOIN tournaments t ON tm.tournament_id = t.id
            WHERE tm.user_id = ?
            ORDER BY tm.joined_at DESC
            """,
            (user_id,)
        ).fetchall()
        conn.close()
        return [
            Tournament(
                id=row['id'],
                name=row['name'],
                code=row['code'],
                created_by=row['created_by'],
                created_at=row['created_at']
            )
            for row in rows
        ]

    @staticmethod
    def delete(tournament_id):
        """刪除房間"""
        conn = get_db_connection()
        try:
            conn.execute("DELETE FROM tournaments WHERE id = ?", (tournament_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
