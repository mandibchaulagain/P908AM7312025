from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from ml.predictor import CropPredictor
from crud.crop import create_prediction, get_all_predictions
from models.crop import CropPredictRequest
from models.user import UserInDB

from auth.security import decode_token, get_current_user

import logging


router = APIRouter(prefix="/api/v1/crop", tags=["Prediction"])
security = HTTPBearer()



# Prediction Endpoint

@router.post("/predict", response_model=Dict[str, Any])
async def predict_crop(
    data: CropPredictRequest,  # <- use the new input model
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # decode token
    token = credentials.credentials
    user_data = decode_token(token)
    if user_data is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    predictor = CropPredictor.get_instance()

    # Use the metrics dict directly
    predictions = predictor.predict(data.metrics)

    user_id = user_data.id

    # Save into DB
    record_id = create_prediction({
        "metrics": {
            "Nitrogen": data.metrics["Nitrogen"],
            "Phosphorous": data.metrics["Phosphorous"],
            "Potassium": data.metrics["Potassium"],
            "Temperature": data.metrics["Temperature"],
            "Rainfall": data.metrics["Rainfall"],
            "Humidity": data.metrics["Humidity"]
        },
        "user_id": user_id,
        "prediction": predictions
    })



    return {
        "record_id": record_id,
        "status": "success",
        "model_version": predictor.model_version,
        "predictions": predictions,
        "user": user_data.username
    }



@router.get("/history")
async def get_prediction_history(limit: int = Query(50, ge=1, le=500)):
    """
    Return the last N crop predictions from the database.
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
