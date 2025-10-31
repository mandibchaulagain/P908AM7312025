import joblib
import numpy as np
from pathlib import Path

class CropPredictor:
    _instance = None
    
    def __init__(self):
        self.rf_model = None
        self.dt_model = None
        self.gbm_model = None
        self.label_encoder = None
        self.feature_names = None
        self.model_version = None

    @classmethod
    def get_instance(cls):
        """Singleton pattern to ensure only one instance of the CropPredictor is loaded."""
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.load_model()
        return cls._instance

    def load_model(self, model_path=None):
        """Load model artifacts from specified path"""
        if model_path is None:
            model_dir = Path(__file__).parent.parent / "model_artifacts"
            
            try:
                with open(model_dir / "latest_model.txt", "r") as f:
                    model_file = f.read().strip()
                model_path = model_dir / model_file
            except FileNotFoundError:
                model_path = model_dir / "latest_model.pkl"
        
        artifacts = joblib.load(model_path)
        self.rf_model = artifacts['rf_model']
        self.dt_model = artifacts['dt_model']
        self.gbm_model = artifacts['gbm_model']  # Load GBM
        self.label_encoder = artifacts['label_encoder']
        self.feature_names = artifacts['feature_names']
        self.model_version = artifacts.get('timestamp', 'unknown')

    def predict(self, data: dict):
        """Make predictions with all models and return ensemble voting result"""
        if self.rf_model is None or self.dt_model is None or self.gbm_model is None:
            self.load_model()
        
        # Validate all required features
        missing_features = [f for f in self.feature_names if f not in data]
        if missing_features:
            raise ValueError(f"Missing features: {', '.join(missing_features)}")
        
        # Prepare input array
        input_array = np.array([data[feature] for feature in self.feature_names]).reshape(1, -1)
        
        # Individual model predictions
        rf_pred = self.rf_model.predict(input_array)[0]
        dt_pred = self.dt_model.predict(input_array)[0]
        gbm_pred = self.gbm_model.predict(input_array)[0]
        
        # Ensemble Voting
        ev_pred = self.ensemble_vote(rf_pred, dt_pred, gbm_pred)
        
        # Decode predictions
        return {
            'rf': self.label_encoder.inverse_transform([rf_pred])[0],
            'dt': self.label_encoder.inverse_transform([dt_pred])[0],
            'gbm': self.label_encoder.inverse_transform([gbm_pred])[0],
            'ev': self.label_encoder.inverse_transform([ev_pred])[0]
        }

    def ensemble_vote(self, rf_pred, dt_pred, gbm_pred):
        """Perform majority voting with tie-breaker based on highest accuracy"""
        votes = [rf_pred, dt_pred, gbm_pred]
        vote_counts = {cls: votes.count(cls) for cls in set(votes)}

        # Majority vote
        max_votes = max(vote_counts.values())
        candidates = [cls for cls, count in vote_counts.items() if count == max_votes]

        if len(candidates) == 1:
            return candidates[0]
        else:
            # Tie-breaker: pick prediction from model with highest accuracy
            accuracy_order = ['gbm', 'rf', 'dt']  # descending accuracy
            for model in accuracy_order:
                pred = {'rf': rf_pred, 'dt': dt_pred, 'gbm': gbm_pred}[model]
                if pred in candidates:
                    return pred
