import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import xgboost as xgb
import lightgbm as lgb
from typing import Dict, Any

from src.application.feature_engineering import FeatureEngineeringPipeline
from src.infrastructure.database.connection import SessionLocal
from src.infrastructure.database.models import ModelMetadata

class TrainingPipeline:
    def __init__(self, data_path: str = "data/processed/processed_students.csv", models_dir: str = "models"):
        self.data_path = data_path
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        self.fe_pipeline = FeatureEngineeringPipeline()

    def train_and_evaluate(self) -> Dict[str, Any]:
        """Loads data, processes features, trains multiple models, and registers the best one"""
        if not os.path.exists(self.data_path):
            from src.application.etl import ETLPipeline
            etl = ETLPipeline()
            etl.run_etl()

        df = pd.read_csv(self.data_path)
        X_train, X_test, y_train, y_test, preprocessor = self.fe_pipeline.prepare_data(df)

        # We will save the preprocessor for predictions
        joblib.dump(preprocessor, os.path.join(self.models_dir, "preprocessor.pkl"))

        models = {
            "RandomForest": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
            "XGBoost": xgb.XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, eval_metric='logloss'),
            "LightGBM": lgb.LGBMClassifier(n_estimators=100, learning_rate=0.05, random_state=42, verbose=-1),
            "ExtraTrees": ExtraTreesClassifier(n_estimators=100, random_state=42),
            "GradientBoosting": GradientBoostingClassifier(random_state=42)
        }

        results = {}
        best_model_name = None
        best_f1 = -1.0
        db = SessionLocal()

        try:
            for name, clf in models.items():
                # Train
                clf.fit(X_train, y_train)
                
                # Predict
                preds = clf.predict(X_test)
                
                # Metrics
                acc = accuracy_score(y_test, preds)
                prec = precision_score(y_test, preds, zero_division=0)
                rec = recall_score(y_test, preds, zero_division=0)
                f1 = f1_score(y_test, preds, zero_division=0)

                results[name] = {
                    "accuracy": float(acc),
                    "precision": float(prec),
                    "recall": float(rec),
                    "f1_score": float(f1)
                }

                # Save model file
                model_path = os.path.join(self.models_dir, f"{name.lower()}_model.pkl")
                joblib.dump(clf, model_path)

                # Database registration
                meta = ModelMetadata(
                    model_name=name,
                    path=model_path,
                    accuracy=float(acc),
                    precision=float(prec),
                    recall=float(rec),
                    f1_score=float(f1),
                    parameters=str(clf.get_params()),
                    is_active=False
                )
                db.add(meta)
                
                if f1 > best_f1:
                    best_f1 = f1
                    best_model_name = name

            db.commit()

            # Set best model as active
            if best_model_name:
                active_model = db.query(ModelMetadata).filter_by(model_name=best_model_name).order_by(ModelMetadata.trained_at.desc()).first()
                if active_model:
                    active_model.is_active = True
                    db.commit()

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

        return {
            "status": "success",
            "best_model": best_model_name,
            "metrics": results
        }

if __name__ == "__main__":
    pipeline = TrainingPipeline()
    res = pipeline.train_and_evaluate()
    print("Training finished:", res)
