from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Asignatura(Base):
    __tablename__ = 'asignaturas'
    id = Column(Integer, primary_key=True)
    codigo_alfa = Column(String(20), unique=True, nullable=False)
    nombre_asignatura = Column(String(200), nullable=False)
    periodo = Column(Integer)

class Estudiante(Base):
    __tablename__ = 'estudiantes'
    id = Column(Integer, primary_key=True)
    id_estudiante = Column(String(20), unique=True, nullable=False) # El ID que usas en el JOIN
    nombre_completo = Column(String(200), nullable=False)

# --- LAS TABLAS QUE FALTAN ---

class Seguimiento(Base):
    __tablename__ = 'seguimiento'
    id = Column(Integer, primary_key=True)
    id_estudiante = Column(String(20), nullable=False)
    codigo_alfa = Column(String(20))
    materia_pendiente = Column(String(200))
    nota = Column(Float, default=0.0)

class MallaCurricular(Base):
    __tablename__ = 'malla_curricular'
    id = Column(Integer, primary_key=True)
    codigo_alfa = Column(String(20), unique=True)
    estado = Column(String(50)) # Ej: 'Construida', 'Pendiente'