from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class Student:
    id: Optional[int]
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
    desertor: bool = False
    prediccion_desercion: Optional[bool] = None
    probabilidad_desercion: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def RIESGO_ALTO(self) -> bool:
        """Domain rule: checks if student is at high risk of dropping out based on key metrics"""
        return self.promedio_acumulado < 3.0 or self.materias_reprobadas >= 3

@dataclass
class Curriculum:
    id: Optional[int]
    codigo_programa: str
    nombre_programa: str
    tasa_empleabilidad: float
    salario_enganche: float
    indice_satisfaccion: float
    nivel_acreditacion: str
    pertinencia_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def calculate_pertinencia(self) -> float:
        """Business rule to calculate academic relevance score (0-100)"""
        weights = {
            "tasa_empleabilidad": 0.4,
            "salario_enganche": 0.3,
            "indice_satisfaccion": 0.2,
            "acreditacion": 0.1
        }
        
        # Normalize acreditacion
        acred_val = 100.0 if "ALTA CALIDAD" in self.nivel_acreditacion.upper() else 60.0
        
        # Max scale salary assumption for normalization: 5,000,000 COP
        norm_salary = min(self.salario_enganche / 5000000.0 * 100.0, 100.0)
        norm_employ = min(self.tasa_empleabilidad * 100.0, 100.0)
        norm_satisfaction = min(self.indice_satisfaccion * 20.0, 100.0)  # assumed 1-5 scale
        
        score = (
            norm_employ * weights["tasa_empleabilidad"] +
            norm_salary * weights["salario_enganche"] +
            norm_satisfaction * weights["indice_satisfaccion"] +
            acred_val * weights["acreditacion"]
        )
        self.pertinencia_score = round(score, 2)
        return self.pertinencia_score
