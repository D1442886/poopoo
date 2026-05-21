from app.models.db import get_db_connection

class Achievement:
    def __init__(self, id, name, description, condition_type, condition_value):
        self.id = id
        self.name = name
        self.description = description
        self.condition_type = condition_type
        self.condition_value = condition_value

    @staticmethod
    def get_all():
        """取得所有成就設定"""
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM achievements").fetchall()
        conn.close()
        return [
            Achievement(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                condition_type=row['condition_type'],
                condition_value=row['condition_value']
            )
            for row in rows
        ]

    @staticmethod
    def get_by_id(achievement_id):
        """取得特定成就"""
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM achievements WHERE id = ?", (achievement_id,)).fetchone()
        conn.close()
        if row:
            return Achievement(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                condition_type=row['condition_type'],
                condition_value=row['condition_value']
            )
        return None


class UserAchievement:
    def __init__(self, id, user_id, achievement_id, unlocked_at=None):
        self.id = id
        self.user_id = user_id
        self.achievement_id = achievement_id
        self.unlocked_at = unlocked_at

    @staticmethod
    def unlock_for_user(user_id, achievement_id):
        """為使用者解鎖成就"""
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT OR IGNORE INTO user_achievements (user_id, achievement_id) VALUES (?, ?)",
                (user_id, achievement_id)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_unlocked_by_user(user_id):
        """取得使用者已解鎖的成就清單"""
        conn = get_db_connection()
        rows = conn.execute(
            """
            SELECT a.*, ua.unlocked_at
            FROM user_achievements ua
            JOIN achievements a ON ua.achievement_id = a.id
            WHERE ua.user_id = ?
            ORDER BY ua.unlocked_at DESC
            """,
            (user_id,)
        ).fetchall()
        conn.close()
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "condition_type": row["condition_type"],
                "condition_value": row["condition_value"],
                "unlocked_at": row["unlocked_at"]
            }
            for row in rows
        ]
