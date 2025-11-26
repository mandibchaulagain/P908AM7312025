#user crud

from database.connection import connection_pool
from auth.utils import get_password_hash

def get_user_by_username(username: str):
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, username, email, password, is_admin, created_at, updated_at FROM users WHERE username = %s",
            (username,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def create_user(username: str, email: str, password: str, is_admin: bool = False):
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    try:
        hashed_password = get_password_hash(password)
        cursor.execute(
            """INSERT INTO users (username, email, password, is_admin)
               VALUES (%s, %s, %s, %s)""",
            (username, email, hashed_password, is_admin)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()