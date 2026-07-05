from flask_login import UserMixin
from src.database.db import get_db

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    @staticmethod
    def get(user_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        if user:
            return User(user["id"], user["username"], user["email"])
        

