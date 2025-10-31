from database.connection import connection_pool
from datetime import datetime
import json

def create_prediction(pred_data: dict):
    """
    Save a crop prediction into the new table.
    pred_data should include keys: nitrogen, phosphorous, potassium,
    temperature, rainfall, humidity, prediction
    """
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """INSERT INTO crop_predictions
            (nitrogen, phosphorous, potassium, temperature, rainfall, humidity, prediction)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                pred_data['Nitrogen'],
                pred_data['Phosphorous'],
                pred_data['Potassium'],
                pred_data['Temperature'],
                pred_data['Rainfall'],
                pred_data['Humidity'],
                json.dumps(pred_data['prediction'])
            )
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_all_predictions(limit: int = 100):
    """
    Return last N predictions
    """
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM crop_predictions ORDER BY created_at DESC LIMIT %s",
            (limit,)
        )
        rows = cursor.fetchall()
        # convert prediction JSON string back to dict
        for row in rows:
            row['prediction'] = json.loads(row['prediction'])
        return rows
    finally:
        cursor.close()
        conn.close()
