#user crud

from database.connection import connection_pool
from auth.utils import get_password_hash

def get_user_by_username(username: str):
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def create_user(username: str, password: str, email: str):
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    try:
        hashed_password = get_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
            (username, hashed_password, email)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()