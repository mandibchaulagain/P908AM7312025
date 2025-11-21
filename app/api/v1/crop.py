from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ml.predictor import CropPredictor
from crud.crop import create_prediction, get_all_predictions
from models.crop import Crop, CropInput
from auth.security import get_current_user
from typing import Any, Dict, List
import logging
from auth.security import decode_token



from models.user import UserInDB
router = APIRouter(prefix="/api/v1/crop", tags=["Prediction"])
security = HTTPBearer()



# Prediction Endpoint

@router.post("/predict", response_model=Dict[str, Any])
async def predict_crop(data: CropInput, current_user: HTTPAuthorizationCredentials = Depends(security)):
    try:
        predictor = CropPredictor.get_instance()

        # Map input fields to match model feature names
        input_data = {
            "Nitrogen": data.Nitrogen,
            "Phosphorous": data.Phosphorous,
            "Potassium": data.Potassium,
            "Temperature": data.Temperature,
            "Rainfall": data.Rainfall,
            "Humidity": data.Humidity
        }

        predictions = predictor.predict(input_data)

        # Save into the new table
        record_id = create_prediction({**input_data, "prediction": predictions})

        return {
            "record_id": record_id,
            "status": "success",
            "model_version": predictor.model_version,
            "predictions": predictions
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Model artifacts not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.get("/history")
async def get_prediction_history(limit: int = Query(50, ge=1, le=500)):
    """
    Return the last N crop predictions from the database.
    Default: last 50 predictions.
    """
    try:
        predictions = get_all_predictions(limit=limit)
        return {
            "status": "success",
            "count": len(predictions),
            "predictions": predictions
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }
