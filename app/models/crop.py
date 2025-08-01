from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CropCreate(BaseModel):
    nitrogen: float
    phosphorous: float
    potassium: float
    temperature: float
    rainfall: float
    humidity: float

class Crop(CropCreate):
    id: int
    user_id: int
    prediction: Optional[str]
    created_at: datetime