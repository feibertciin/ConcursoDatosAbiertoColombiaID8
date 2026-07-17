from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Student, Curriculum

class StudentRepository(ABC):
    @abstractmethod
    def save(self, student: Student) -> Student:
        pass

    @abstractmethod
    def get_by_id(self, student_id: int) -> Optional[Student]:
        pass

    @abstractmethod
    def list_all(self) -> List[Student]:
        pass

class CurriculumRepository(ABC):
    @abstractmethod
    def save(self, curriculum: Curriculum) -> Curriculum:
        pass

    @abstractmethod
    def get_by_code(self, code: str) -> Optional[Curriculum]:
        pass

    @abstractmethod
    def list_all(self) -> List[Curriculum]:
        pass

class PredictiveModel(ABC):
    @abstractmethod
    def train(self, data_path: str) -> dict:
        pass

    @abstractmethod
    def predict(self, features: dict) -> dict:
        pass

    @abstractmethod
    def explain(self, instance: dict) -> dict:
        pass
