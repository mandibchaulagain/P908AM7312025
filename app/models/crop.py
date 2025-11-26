from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict, Optional

# class CropInput(BaseModel):
#     Nitrogen: float = Field(..., example=90)
#     Phosphorous: float = Field(..., example=40)
#     Potassium: float = Field(..., example=40)
#     Temperature: float = Field(..., example=26.5)
#     Rainfall: float = Field(..., example=200.0)
#     Humidity: float = Field(..., example=80.0)


# class Crop(BaseModel):
#     id: int
#     metrics: dict            # dynamic metrics!
#     prediction: dict
#     created_at: datetime

class CropPredictRequest(BaseModel):
    metrics: Dict[str, float]  # dynamic input, e.g., {"Nitrogen": 180, ...}

class CropPredictResponse(BaseModel):
    id: int
    metrics: Dict[str, float]
    prediction: Dict[str, Any]
    created_at: str