import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "mercador_rt")

# String de conexión para PostgreSQL usando psycopg2
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    print(f"Error al inicializar configurador SQLAlchemy: {e}")
    # Fallback to create dummy Base to avoid crash at import time if PG is missing
    Base = declarative_base()

def init_db():
    from . import models_db
    print("Inicializando Base de Datos e intentando migrar tablas (Fase 5)...")
    try:
        # Producción/Estable: Solo crea tablas si no existen. Base de datos persistente.
        Base.metadata.create_all(bind=engine)
        print("Tablas de BD conectadas exitosamente.")
    except Exception as e:
        print(f"Error crítico conectando a PostgreSQL.")
        print(f"Detalles: {e}")
        print("Asegurate de que Postgres está corriendo y la database existe.")
        raise
