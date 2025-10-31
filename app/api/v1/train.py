import os
import joblib
import pandas as pd
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from typing import Dict
from collections import Counter

# Import your custom models
from ml.model import RandomForest
from ml.decision_model import DecisionTreeClassifier
from ml.gradient_boosting import FastGBMClassifier

router = APIRouter(prefix="/api/v1/train")
security = HTTPBearer()


# Ensemble Voting
def majority_vote(preds_list):
    """Perform majority voting across model predictions"""
    voted_preds = []
    for votes in zip(*preds_list):
        vote_counts = Counter(votes)
        majority = max(vote_counts, key=vote_counts.get)
        if len(vote_counts) == 3:  # all disagree -> default to Random Forest
            majority = votes[0]  # assume first is RandomForest
        voted_preds.append(majority)
    return np.array(voted_preds)


# Background Training Task

def train_model_task(model_dir: str, data_path: str):
    try:
        
        # Load and preprocess
        
        df = pd.read_csv(data_path)
        label_encoder = LabelEncoder()
        df['Label'] = label_encoder.fit_transform(df['Label'])

        features = ['Nitrogen', 'Phosphorous', 'Potassium',
                    'Temperature', 'Rainfall', 'Humidity']

        X = df[features].values
        y = df['Label'].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        
        # Train Random Forest
        
        print("Training Random Forest...")
        rf = RandomForest(
            n_estimators=100,
            max_features='sqrt',
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            oob_score=True
        )
        rf.fit(X_train, y_train)
        rf_pred = rf.predict(X_test)

        
        # Train Decision Tree
        
        print("Training Decision Tree...")
        dt = DecisionTreeClassifier(
            criterion='entropy',
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            max_features='sqrt',
            ccp_alpha=0.01
        )
        dt.fit(X_train, y_train)
        dt_pred = dt.predict(X_test)

        
        # Train Gradient Boosting (GBM)
        
        print("Training Gradient Boosting...")
        gbm = FastGBMClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            subsample=0.8,
            n_feature_samples='sqrt',
            early_stopping_rounds=10
        )
        gbm.fit(X_train, y_train)
        gbm_pred = gbm.predict(X_test)

        # Ensemble Voting

        ensemble_pred = majority_vote([rf_pred, dt_pred, gbm_pred])


        # Evaluation Metrics

        def get_metrics(y_true, y_pred):
            return {
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, average='macro'),
                'recall': recall_score(y_true, y_pred, average='macro'),
                'f1': f1_score(y_true, y_pred, average='macro')
            }

        results = {
            'random_forest': get_metrics(y_test, rf_pred),
            'decision_tree': get_metrics(y_test, dt_pred),
            'gbm': get_metrics(y_test, gbm_pred),
            'ensemble': get_metrics(y_test, ensemble_pred),
        }

        
        # Save Model Artifacts
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_file = f"model_{timestamp}.pkl"
        os.makedirs(model_dir, exist_ok=True)

        joblib.dump({
            'rf_model': rf,
            'dt_model': dt,
            'gbm_model': gbm,
            'label_encoder': label_encoder,
            'feature_names': features,
            'metrics': results,
            'timestamp': timestamp,
            'training_samples': len(df),
            'default_humidity': df['Humidity'].median(),
        }, os.path.join(model_dir, model_file))

        # Update latest model reference
        with open(os.path.join(model_dir, "latest_model.txt"), "w") as f:
            f.write(model_file)

        print(f"✅ Model training complete. Saved to {model_file}")
        print("📊 Results Summary:")
        for name, metrics in results.items():
            print(f"{name.upper()}: {metrics}")

    except Exception as e:
        error_path = os.path.join(model_dir, "training_error.log")
        with open(error_path, "a") as f:
            f.write(f"{datetime.now()}: {str(e)}\n")
        raise


# API Endpoint

@router.post("/training", response_model=Dict[str, str])
async def train_model(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(security)
):
    """Trigger background training of RandomForest, DecisionTree, and GBM models"""
    # Uncomment if you want admin restriction:
    # if current_user.get("role") != "admin":
    #     raise HTTPException(403, detail="Admin access required")

    model_dir = os.path.join(os.path.dirname(__file__), "./../../model_artifacts")
    data_path = os.path.join(os.path.dirname(__file__), "./../../data/montecarlo_crop_data_noisy.csv")

    if not os.path.exists(data_path):
        raise HTTPException(404, detail="Training data not found")

    background_tasks.add_task(train_model_task, model_dir, data_path)
    return {"message": "Background model training (RF + DT + GBM + Ensemble) started successfully."}
