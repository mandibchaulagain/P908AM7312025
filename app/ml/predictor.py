import os
import joblib
import numpy as np
from pathlib import Path
from .model import RandomForest

class CropPredictor:
    _instance = None
    
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.feature_names = None
        self.model_version = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.load_model()
        return cls._instance

    def load_model(self, model_path=None):
        """Load model from specified path"""
        if model_path is None:
            model_dir = Path(__file__).parent.parent / "model_artifacts"
            try:
                with open(model_dir / "latest_model.txt") as f:
                    model_file = f.read().strip()
                model_path = model_dir / model_file
            except FileNotFoundError:
                model_path = model_dir / "latest_model.pkl"
        
        artifacts = joblib.load(model_path)
        self.model = artifacts['model']
        self.label_encoder = artifacts['label_encoder']
        self.feature_names = artifacts['feature_names']
        self.model_version = artifacts.get('timestamp', 'unknown')

    def predict(self, data: dict):
        if self.model is None:
            self.load_model()
        
        # Convert keys to match model's expected features
        converted_data = {
            feat: data[feat.lower()] 
            for feat in self.feature_names
        }
        
        # Validate all required features are present
        missing = set(self.feature_names) - set(converted_data.keys())
        if missing:
            raise ValueError(f"Missing features: {missing}")
        
        input_array = np.array([[converted_data[f] for f in self.feature_names]])
        prediction = self.model.predict(input_array)
        return self.label_encoder.inverse_transform(prediction)[0]