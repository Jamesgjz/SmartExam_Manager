from sqlalchemy import create_engine, Column, String, Integer, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. TUS CREDENCIALES DE NEON (Las mismas del seed anterior)
USER = "neondb_owner"
PASS = "npg_VPz8RYwQ7Gxs"
HOST = "ep-misty-dream-aplxjl8l-pooler.c-7.us-east-1.aws.neon.tech"
NAME = "neondb"

# URL con SSL forzado
url = f"postgresql://{USER}:{PASS}@{HOST}:5432/{NAME}?sslmode=require"
engine = create_engine(url)
Base = declarative_base()

# 2. DEFINICIÓN DE LAS TABLAS FALTANTES (Tal cual las pide tu SQL)
class Estudiante(Base):
    __tablename__ = 'estudiantes'
    id = Column(Integer, primary_key=True)
    id_estudiante = Column(String(20), unique=True)
    nombre_completo = Column(String(200))

class Seguimiento(Base):
    __tablename__ = 'seguimiento'
    id = Column(Integer, primary_key=True)
    id_estudiante = Column(String(20))
    codigo_alfa = Column(String(20))
    materia_pendiente = Column(String(200))
    nota = Column(Float, default=0.0)

class MallaCurricular(Base):
    __tablename__ = 'malla_curricular'
    id = Column(Integer, primary_key=True)
    codigo_alfa = Column(String(20), unique=True)
    estado = Column(String(50))

def run_fix():
    print(f"Conectando a Neon para crear tablas de reporte...")
    try:
        # Crea físicamente las tablas en la nube
        Base.metadata.create_all(bind=engine)
        
        # Verificación final
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("\n🚀 ¡TABLAS 'seguimiento' Y 'malla_curricular' CREADAS!")
        print("Ahora la consulta SQL de reportes ya tiene de dónde leer.")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    run_fix()