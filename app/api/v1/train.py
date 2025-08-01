import os
import joblib
import pandas as pd
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer
from datetime import datetime
from ml.model import RandomForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from typing import Dict

router = APIRouter(prefix="/api/v1/train")
security = HTTPBearer()

def train_model_task(model_dir: str, data_path: str):
    """Background task for model training"""
    try:
        # Load and preprocess data
        df = pd.read_csv(data_path)
        label_encoder = LabelEncoder()
        df['Label'] = label_encoder.fit_transform(df['Label'])
        features = ['Nitrogen', 'Phosphorous', 'Potassium', 
                   'Temperature', 'Rainfall', 'Humidity']
        
        # Train-test split
        X = df[features].values
        y = df['Label'].values
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        rf = RandomForest(
            n_estimators=100,
            max_features='sqrt',
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            oob_score=True
        )
        rf.fit(X_train, y_train)
        
        # Evaluate
        y_pred = rf.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Save artifacts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_file = f"model_{timestamp}.pkl"
        
        joblib.dump({
            'model': rf,
            'label_encoder': label_encoder,
            'feature_names': features,
            'feature_importances': dict(zip(features, rf.feature_importances)),
            'class_names': label_encoder.classes_,
            'timestamp': timestamp,
            'accuracy': accuracy,
            'default_humidity': df['Humidity'].median()
        }, os.path.join(model_dir, model_file))
        
        # Update latest model reference
        with open(os.path.join(model_dir, "latest_model.txt"), "w") as f:
            f.write(model_file)
            
    except Exception as e:
        # Log error for debugging
        with open(os.path.join(model_dir, "training_error.log"), "a") as f:
            f.write(f"{datetime.now()}: {str(e)}\n")
        raise

@router.post("/training", response_model=Dict[str, str])
async def train_model(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(security)
):
    # """Endpoint to trigger model training"""
    # if current_user.get("role") != "admin":
    #     raise HTTPException(403, detail="Admin access required")
    
    model_dir = os.path.join(os.path.dirname(__file__), "./../../model_artifacts")
    data_path = os.path.join(os.path.dirname(__file__), "./../../data/montecarlo_crop_data_noisy.csv")
    
    if not os.path.exists(data_path):
        raise HTTPException(404, detail="Training data not found")
    
    background_tasks.add_task(train_model_task, model_dir, data_path)
    
    return {"message": "Model training started in background"}