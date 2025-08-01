from database.connection import connection_pool
from datetime import datetime

def create_crop(crop_data: dict, user_id: int):
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """INSERT INTO crops 
            (user_id, nitrogen, phosphorous, potassium, 
             temperature, rainfall, humidity, prediction)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (user_id, crop_data['nitrogen'], crop_data['phosphorous'],
             crop_data['potassium'], crop_data['temperature'],
             crop_data['rainfall'], crop_data['humidity'],
             crop_data.get('prediction')))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def get_user_crops(user_id: int):
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM crops WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()