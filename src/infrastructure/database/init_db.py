from .connection import Base, engine
from .models import StudentModel, CurriculumModel, ModelMetadata

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")

if __name__ == "__main__":
    init_db()
