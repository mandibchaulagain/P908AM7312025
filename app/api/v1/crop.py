from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from ml.predictor import CropPredictor
from crud.crop import create_crop, get_user_crops
from models.crop import CropCreate, Crop
from auth.security import get_current_user
from typing import List

from models.user import UserInDB

router = APIRouter(prefix="/api/v1/crop")

@router.post("/predict", response_model=Crop)
async def predict_crop(
    crop_data: CropCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    predictor = CropPredictor.get_instance()
    try:
        # Convert input to dict for prediction
        input_data = crop_data.dict()
        
        # Get prediction
        prediction = predictor.predict(input_data)
        
        # Save to database
        crop_id = create_crop(
            {**input_data, "prediction": prediction},
            current_user.id
        )
        
        # Return created crop as Pydantic model
        return Crop(
            id=crop_id,
            user_id=current_user.id,
            prediction=prediction,
            created_at=datetime.utcnow(),
            **input_data
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/history", response_model=List[Crop])
async def get_history(
    current_user: UserInDB = Depends(get_current_user)
):
    # Access id as an attribute, not like a dict
    return get_user_crops(current_user.id)