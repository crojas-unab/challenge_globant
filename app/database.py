from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base  # o from .models import Base si estás en la misma carpeta

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

