import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
import joblib

from src.infrastructure.database.connection import get_db, SessionLocal
from src.infrastructure.database.models import StudentModel, ModelMetadata, CurriculumModel
from src.application.training import TrainingPipeline
from src.application.xai import ExplainabilityEngine
from pydantic import BaseModel

app = FastAPI(
    title="Framework-ML-SNIES API",
    description="API de Predicción de Permanencia Estudiantil e Integración de Datos Académicos",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StudentPredictionInput(BaseModel):
    nombre: str
    genero: str
    departamento_origen: str
    estrato_socioeconomico: int
    tipo_colegio: str
    programa_academico: str
    edad: int
    puntaje_saber11: float
    promedio_acumulado: float
    materias_reprobadas: int
    ingreso_familiar: float

@app.get("/")
def read_root():
    return {"message": "API de Framework-ML-SNIES activa y funcional."}

@app.post("/predict")
def predict_student(student: StudentPredictionInput, db: Session = Depends(get_db)):
    # 1. Load active model
    active_model = db.query(ModelMetadata).filter_by(is_active=True).order_by(ModelMetadata.trained_at.desc()).first()
    if not active_model:
        # Fallback to RF if none active
        active_model = db.query(ModelMetadata).filter_by(model_name="RandomForest").order_by(ModelMetadata.trained_at.desc()).first()
    
    if not active_model or not os.path.exists(active_model.path):
        raise HTTPException(status_code=400, detail="No active trained model found. Please train models first.")

    preprocessor_path = "models/preprocessor.pkl"
    if not os.path.exists(preprocessor_path):
        raise HTTPException(status_code=400, detail="Preprocessor not found.")

    model = joblib.load(active_model.path)
    preprocessor = joblib.load(preprocessor_path)

    # 2. Preprocess input
    input_data = pd.DataFrame([student.model_dump()])
    proc_data = preprocessor.transform(input_data)

    # 3. Predict
    prob = float(model.predict_proba(proc_data)[0][1])
    pred = bool(model.predict(proc_data)[0])

    # 4. Save student prediction history
    std_db = StudentModel(
        nombre=student.nombre,
        genero=student.genero,
        departamento_origen=student.departamento_origen,
        estrato_socioeconomico=student.estrato_socioeconomico,
        tipo_colegio=student.tipo_colegio,
        programa_academico=student.programa_academico,
        edad=student.edad,
        puntaje_saber11=student.puntaje_saber11,
        promedio_acumulado=student.promedio_acumulado,
        materias_reprobadas=student.materias_reprobadas,
        ingreso_familiar=student.ingreso_familiar,
        desertor=False,
        prediccion_desercion=pred,
        probabilidad_desercion=prob
    )
    db.add(std_db)
    db.commit()

    return {
        "prediccion_desercion": pred,
        "probabilidad_desercion": prob,
        "modelo_utilizado": active_model.model_name
    }

@app.post("/train")
def run_training():
    try:
        pipeline = TrainingPipeline()
        res = pipeline.train_and_evaluate()
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    models_meta = db.query(ModelMetadata).all()
    return [{
        "id": m.id,
        "model_name": m.model_name,
        "accuracy": m.accuracy,
        "precision": m.precision,
        "recall": m.recall,
        "f1_score": m.f1_score,
        "is_active": m.is_active,
        "trained_at": m.trained_at
    } for m in models_meta]

@app.post("/explain")
def explain_instance(student: StudentPredictionInput):
    try:
        engine = ExplainabilityEngine()
        input_data = pd.DataFrame([student.model_dump()])
        explanation = engine.get_local_explanation_lime(input_data, "data/processed/processed_students.csv")
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
