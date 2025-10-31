from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CropInput(BaseModel):
    Nitrogen: float = Field(..., example=90)
    Phosphorous: float = Field(..., example=40)
    Potassium: float = Field(..., example=40)
    Temperature: float = Field(..., example=26.5)
    Rainfall: float = Field(..., example=200.0)
    Humidity: float = Field(..., example=80.0)

class Crop(CropInput):
    id: int
    user_id: int
    prediction: Optional[str]
    created_at: datetime