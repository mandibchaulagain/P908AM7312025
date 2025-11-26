from database.connection import connection_pool
import json

def create_prediction(pred_data: dict):
    """
    pred_data must include:
      - metrics fields: Nitrogen, Phosphorous, Potassium, Temperature, Rainfall, Humidity
      - prediction: dict
    """

    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Step 1: Insert into predictions table
        cursor.execute(
            "INSERT INTO predictions (prediction) VALUES (%s)",
            (json.dumps(pred_data["prediction"]),)
        )
        prediction_id = cursor.lastrowid

        # Step 2: Fetch metric IDs from metric_types
        cursor.execute("SELECT id, name FROM metric_types")
        metric_map = {row["name"].lower(): row["id"] for row in cursor.fetchall()}

        # Step 3: Insert each measurement
        metric_fields = [
            "Nitrogen", "Phosphorous", "Potassium",
            "Temperature", "Rainfall", "Humidity"
        ]

        for field in metric_fields:
            metric_key = field.lower()
            if metric_key not in metric_map:
                raise ValueError(f"Metric type '{metric_key}' not found in metric_types.")

            metric_id = metric_map[metric_key]
            value = float(pred_data[field])

            cursor.execute(
                """INSERT INTO measurements (prediction_id, metric_id, value)
                   VALUES (%s, %s, %s)""",
                (prediction_id, metric_id, value)
            )

        conn.commit()
        return prediction_id

    finally:
        cursor.close()
        conn.close()



def get_all_predictions(limit: int = 100):
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # First: get predictions
        cursor.execute(
            "SELECT id, prediction, created_at FROM predictions ORDER BY created_at DESC LIMIT %s",
            (limit,)
        )
        predictions = cursor.fetchall()

        # Load JSON field
        for p in predictions:
            p["prediction"] = json.loads(p["prediction"])

        # Fetch all measurements for the returned predictions
        prediction_ids = tuple(p["id"] for p in predictions)
        if not prediction_ids:
            return []

        query = f"""
            SELECT m.prediction_id, t.name AS metric, m.value
            FROM measurements m
            JOIN metric_types t ON m.metric_id = t.id
            WHERE m.prediction_id IN ({','.join(['%s'] * len(prediction_ids))})
        """

        cursor.execute(query, prediction_ids)
        measurement_rows = cursor.fetchall()

        # Group metrics per prediction
        for row in measurement_rows:
            for p in predictions:
                if p["id"] == row["prediction_id"]:
                    p.setdefault("metrics", {})[row["metric"]] = row["value"]

        return predictions

    finally:
        cursor.close()
        conn.close()
