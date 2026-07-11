from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from .connection import Base

class StudentModel(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    genero = Column(String)
    departamento_origen = Column(String)
    estrato_socioeconomico = Column(Integer)
    tipo_colegio = Column(String)
    programa_academico = Column(String)
    edad = Column(Integer)
    puntaje_saber11 = Column(Float)
    promedio_acumulado = Column(Float)
    materias_reprobadas = Column(Integer)
    ingreso_familiar = Column(Float)
    
    # Target label
    desertor = Column(Boolean, default=False)
    
    # Prediction results
    prediccion_desercion = Column(Boolean, nullable=True)
    probabilidad_desercion = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class CurriculumModel(Base):
    __tablename__ = "curriculums"

    id = Column(Integer, primary_key=True, index=True)
    codigo_programa = Column(String, unique=True, index=True)
    nombre_programa = Column(String)
    tasa_empleabilidad = Column(Float)  # OLE data integration
    salario_enganche = Column(Float)     # OLE data integration
    indice_satisfaccion = Column(Float)
    nivel_acreditacion = Column(String) # SNIES
    pertinencia_score = Column(Float, nullable=True) # Calulated score
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ModelMetadata(Base):
    __tablename__ = "model_metadata"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, index=True)  # e.g., "RandomForest", "XGBoost"
    run_id = Column(String, nullable=True)      # MLflow run id
    path = Column(String)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    parameters = Column(String) # JSON or string configurations
    trained_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=False)
