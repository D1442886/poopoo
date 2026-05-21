from app.models.db import get_db_connection

class Record:
    def __init__(self, id, user_id, bristol_type, color, duration=None, notes=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.bristol_type = bristol_type
        self.color = color
        self.duration = duration
        self.notes = notes
        self.created_at = created_at

    @staticmethod
    def create(user_id, bristol_type, color, duration=None, notes=None):
        """新增排便紀錄"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO records (user_id, bristol_type, color, duration, notes) VALUES (?, ?, ?, ?, ?)",
                (user_id, bristol_type, color, duration, notes)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_by_id(record_id):
        """取得單筆紀錄"""
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM records WHERE id = ?", (record_id,)).fetchone()
        conn.close()
        if row:
            return Record(
                id=row['id'],
                user_id=row['user_id'],
                bristol_type=row['bristol_type'],
                color=row['color'],
                duration=row['duration'],
                notes=row['notes'],
                created_at=row['created_at']
            )
        return None

    @staticmethod
    def get_by_user_id(user_id):
        """取得某個使用者的所有排便紀錄（時間降序）"""
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT * FROM records WHERE user_id = ? ORDER BY created_at DESC", 
            (user_id,)
        ).fetchall()
        conn.close()
        return [
            Record(
                id=row['id'],
                user_id=row['user_id'],
                bristol_type=row['bristol_type'],
                color=row['color'],
                duration=row['duration'],
                notes=row['notes'],
                created_at=row['created_at']
            )
            for row in rows
        ]

    @staticmethod
    def get_recent_by_user_id(user_id, limit=7):
        """取得某個使用者最近 N 筆紀錄"""
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT * FROM records WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", 
            (user_id, limit)
        ).fetchall()
        conn.close()
        return [
            Record(
                id=row['id'],
                user_id=row['user_id'],
                bristol_type=row['bristol_type'],
                color=row['color'],
                duration=row['duration'],
                notes=row['notes'],
                created_at=row['created_at']
            )
            for row in rows
        ]

    @staticmethod
    def get_all():
        """取得全系統所有紀錄"""
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM records ORDER BY created_at DESC").fetchall()
        conn.close()
        return [
            Record(
                id=row['id'],
                user_id=row['user_id'],
                bristol_type=row['bristol_type'],
                color=row['color'],
                duration=row['duration'],
                notes=row['notes'],
                created_at=row['created_at']
            )
            for row in rows
        ]

    @staticmethod
    def delete(record_id):
        """刪除單筆紀錄"""
        conn = get_db_connection()
        try:
            conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
