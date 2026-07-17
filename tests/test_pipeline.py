import os
import pandas as pd
import pytest
from src.application.etl import ETLPipeline
from src.application.feature_engineering import FeatureEngineeringPipeline

def test_etl_pipeline():
    # Setup paths
    raw_dir = "data/raw_test"
    processed_dir = "data/processed_test"
    
    pipeline = ETLPipeline(raw_dir=raw_dir, processed_dir=processed_dir)
    students, curriculum = pipeline.run_etl()
    
    # Assert files are created
    assert os.path.exists(os.path.join(processed_dir, "processed_students.csv"))
    assert os.path.exists(os.path.join(processed_dir, "processed_curriculum.csv"))
    
    # Assert dataframes are not empty
    assert len(students) > 0
    assert len(curriculum) > 0
    
    # Cleanup test files
    for f in ["snies_matriculados.csv", "dane_socioeconomico.csv", "ole_graduados.csv", "colombia_datos_abiertos.csv"]:
        path = os.path.join(raw_dir, f)
        if os.path.exists(path):
            os.remove(path)
    for f in ["processed_students.csv", "processed_curriculum.csv"]:
        path = os.path.join(processed_dir, f)
        if os.path.exists(path):
            os.remove(path)
            
    if os.path.exists(raw_dir):
        os.rmdir(raw_dir)
    if os.path.exists(processed_dir):
        os.rmdir(processed_dir)

def test_feature_engineering():
    # Make a dummy dataframe
    df = pd.DataFrame({
        "edad": [20, 22, 19, 21, 23],
        "puntaje_saber11": [320, 280, 350, 290, 310],
        "promedio_acumulado": [3.8, 3.2, 4.5, 2.8, 3.6],
        "materias_reprobadas": [0, 1, 0, 2, 0],
        "ingreso_familiar": [2000000.0, 1500000.0, 4000000.0, 1200000.0, 2500000.0],
        "genero": ["MASCULINO", "FEMENINO", "MASCULINO", "FEMENINO", "MASCULINO"],
        "departamento_origen": ["BOGOTA D.C.", "ANTIOQUIA", "VALLE DEL CAUCA", "ATLANTICO", "SANTANDER"],
        "estrato_socioeconomico": [3, 2, 4, 1, 3],
        "tipo_colegio": ["OFICIAL", "NO OFICIAL", "NO OFICIAL", "OFICIAL", "OFICIAL"],
        "programa_academico": ["INGENIERIA DE SISTEMAS", "MEDICINA", "DERECHO", "ADMINISTRACION DE EMPRESAS", "PSICOLOGIA"],
        "desertor": [0, 1, 0, 1, 0]
    })
    
    fe = FeatureEngineeringPipeline()
    X_tr, X_te, y_tr, y_te, _ = fe.prepare_data(df)
    
    # Assert shapes are valid
    assert X_tr.shape[0] == 4
    assert X_te.shape[0] == 1
